import urllib.request
import csv
from google.cloud import bigquery
from google.oauth2 import service_account # Or use default credentials
import io


PROJECT_ID = "your-gcp-project-id"
DATASET_ID = "your_dataset_id"
TABLE_ID = "your_table_id"



CSV_URL = "https://data.gov.au/data/dataset/bc515135-4bb6-4d50-957a-3713709a76d3/resource/55ad4b1c-5eeb-44ea-8b29-d410da431be3/download/business_names_202505.csv"

def fetch_csv_data(url):
    """Fetches CSV data from a given URL."""
    print(f"Fetching CSV data from: {url}")
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                try:
                    return io.TextIOWrapper(response, encoding='utf-8')
                except UnicodeDecodeError:
                    print("UTF-8 decoding failed")
                    with urllib.request.urlopen(url) as response_retry:
                         return io.TextIOWrapper(response_retry, encoding='latin-1')

            else:
                print(f"Error fetching data: HTTP {response.status}")
                return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during fetch: {e}")
        return None

def load_data_to_bigquery(project_id, dataset_id, table_id, csv_file_object):
    #Loads data from a CSV file object into a BigQuery table
    try:
        client = bigquery.Client(project=project_id)
        print(f"BigQuery client initialized for project: {project_id}")
    except Exception as e:
        print(f"Error initializing BigQuery client: {e}")
        print("Ensure you have authenticated with Google Cloud SDK (e.g., 'gcloud auth application-default login')")
        print("or provided a valid service account key.")
        return

    try:
        csv_reader = csv.reader(csv_file_object)
        header = next(csv_reader) 
        print(f"CSV Header: {header}")

        csv_file_object.seek(0)
        next(csv_reader)

        schema = []
        date_columns = ["BN_REG_DT", "BN_CANCEL_DT", "BN_RENEW_DT"]
        for column_name in header:
            col_name_cleaned = column_name.replace(" ", "_").replace("(", "").replace(")", "") #remove spaces and parentheses
            if column_name in date_columns:
                schema.append(bigquery.SchemaField(col_name_cleaned, "STRING", mode="NULLABLE")) #load as string as csv data type can be unreliable
            elif column_name == "BN_ABN": 
                schema.append(bigquery.SchemaField(col_name_cleaned, "STRING", mode="NULLABLE"))
            else:
                schema.append(bigquery.SchemaField(col_name_cleaned, "STRING", mode="NULLABLE"))

        print(f"Inferred Schema for BigQuery: {schema}")

    except StopIteration:
        print("CSV file appears to be empty or has no header.")
        return
    except Exception as e:
        print(f"Error processing CSV header or defining schema: {e}")
        return

    # --- Configure Load Job ---
    table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
    job_config = bigquery.LoadJobConfig()
    job_config.schema = schema
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.skip_leading_rows = 1  # Skip the header row in the CSV file
    job_config.autodetect = False 
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE # its a full refresh each time no inrementals or merges

    # --- Load Data ---
    try:
        print(f"Loading data into BigQuery table: {project_id}.{dataset_id}.{table_id}")
        binary_file_object = csv_file_object.buffer

        load_job = client.load_table_from_file(
            binary_file_object, 
            table_ref,
            job_config=job_config
        )
        print(f"Starting job: {load_job.job_id}")

        load_job.result() 
        print("Job finished.")

        destination_table = client.get_table(table_ref)
        print(f"Loaded {destination_table.num_rows} rows into {dataset_id}.{table_id}")

    except Exception as e:
        print(f"Error loading data to BigQuery: {e}")
        if hasattr(e, 'errors') and e.errors:
            for error in e.errors:
                print(f"  Error detail: {error['message']} at {error.get('location', 'N/A')}")


if __name__ == "__main__":
    if PROJECT_ID == "your-gcp-project-id" or DATASET_ID == "your_dataset_id" or TABLE_ID == "your_table_id":
        print("Please update PROJECT_ID, DATASET_ID, and TABLE_ID in the script.")
    else:

        text_file_wrapper = fetch_csv_data(CSV_URL)

        if text_file_wrapper:
            try:
                load_data_to_bigquery(PROJECT_ID, DATASET_ID, TABLE_ID, text_file_wrapper)
            finally:
                text_file_wrapper.close()
                print("CSV file object closed.")
