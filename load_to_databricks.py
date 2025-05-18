import urllib.request
import io
import os
import tempfile
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DateType
from pyspark.sql.functions import col, to_date
import pandas as pd


CSV_URL = "https://data.gov.au/data/dataset/bc515135-4bb6-4d50-957a-3713709a76d3/resource/55ad4b1c-5eeb-44ea-8b29-d410da431be3/download/business_names_202505.csv"


DATABRICKS_CATALOG = {Your Catalog Name}
DATABRICKS_SCHEMA = {you schema}    
DATABRICKS_TABLE_NAME = "business_names_australia"



with urllib.request.urlopen(CSV_URL) as response:
    if response.status == 200:
        content_bytes = response.read()

    print("Attempting to decode with UTF-8...")
    if content_bytes.startswith(b'\xef\xbb\xbf'):  # Check for BOM
        source_encoding = 'utf-8-sig'
        print("UTF-8 with BOM detected.")
    else:
        source_encoding = 'utf-8'
    decoded_content = content_bytes.decode(source_encoding)
    print(f"Successfully decoded with {source_encoding}.")

    # Read the CSV content
    df_pd = pd.read_csv(io.StringIO(decoded_content), delimiter='\t', error_bad_lines=False)
    
    # Replace invalid characters in column names
    df_pd.columns = [col.replace(' ', '_').replace(',', '_').replace(';', '_')
                     .replace('(', '_').replace(')', '_').replace('{', '_')
                     .replace('}', '_').replace('', '_').replace('\t', '_')
                     .replace('=', '_') for col in df_pd.columns]

    # Create Spark DataFrame
    df = spark.createDataFrame(df_pd)
    df.show()
    
    df.write.format("delta").mode("overwrite").saveAsTable(f"{DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.{DATABRICKS_TABLE_NAME}")
