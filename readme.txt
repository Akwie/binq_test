
# CKAN Search API Documentation

This document provides instructions on how to set up, run, and use the CKAN Search API. This API acts as a proxy to interact with a CKAN data portal (e.g., data.gov.au) to search for records within specific datasets.

## 1. Overview

The API provides a single endpoint (`/search`) that accepts POST requests with a JSON payload. This payload specifies the search criteria, including general queries, exact match filters, the target CKAN resource ID, and the desired number of results.

## 2. Setup and Running the API

### Prerequisites
* Python 3.x
* Flask (`pip install Flask`)
* ckanapi (`pip install ckanapi`)
All the above are in the requirements.txt file and will auto install with docker image

### Environment Variables
The API relies on the following environment variables:

* **`API_TOKEN` (Required)**: Your API key for the CKAN instance. The script will default to"YOUR_API_TOKEN"` place holder as it doesn't seem like it requires a token. But documentation expects it.
    * Example: `export API_TOKEN="your_actual_ckan_api_key"`
* **`CKAN_INSTANCE_URL` (Optional)**: The base URL of the CKAN instance.
    * Defaults to: `https://www.data.gov.au/data/`
    * Example: `export CKAN_INSTANCE_URL="https://your.ckan.instance.url/"`
* **`RESOURCE_ID` (Optional, but often needed for specific datasets)**: A default CKAN resource ID to search against if not provided in the request body. The script comments this out by default, but the `/search` endpoint has its own default.
    * Default in `/search` endpoint if not in request: `55ad4b1c-5eeb-44ea-8b29-d410da431be3` (Business Names dataset on data.gov.au)
    * Example: `export RESOURCE_ID="your_default_resource_id"`
* **`PORT` (Optional)**: The port on which the Flask application will run.
    * Defaults to: `8080`
    * Example: `export PORT="5000"`

### Running the Application
1.  Save the Python script (e.g., as `main.py`).
2.  Set the required environment variables in your terminal.
3.  Run the script: `python main.py`
4.  The API will be accessible at `http://0.0.0.0:PORT/` (e.g., `http://0.0.0.0:8080/`).

## 3. API Endpoint: `/search`

* **Method**: `POST`
* **Content-Type**: `application/json`
* **Description**: Searches records in a specified CKAN resource.

### Request Body (JSON)


| Parameter     | Type   | Required/Optional | Default Value                               | Description                                                                                                |
| :------------ | :----- | :---------------- | :------------------------------------------ | :--------------------------------------------------------------------------------------------------------- |
| `query`       | string | Optional          | `null`                                      | A general search term. CKAN's `datastore_search` uses this for "like" or partial matches across fields.    |
| `filters`     | object | Optional          | `{}`                                        | A dictionary of field-value pairs for exact matches. E.g., `{"State": "NSW", "Status": "Registered"}`. |
| `limit`       | integer| Optional          | `5`                                         | The maximum number of records to return.                                                                   |
| `resource_id` | string | Optional          | `55ad4b1c-5eeb-44ea-8b29-d410da431be3`       | The unique identifier of the CKAN resource (dataset file) to search within.                                |

**Note**: At least one of `query` or `filters` must be provided in the request.

### Success Response (200 OK)
Returns a JSON array of records matching the search criteria.
```json
[
    {
        "ABN": "12345678901",
        "BN_CANCEL_DT": null,
        "BN_REG_DT": "2020-01-15T00:00:00",
        "BN_RENEW_DT": "2023-01-15T00:00:00",
        "BN_STATE_NUM": "NSW",
        "BN_STATE_OF_REG": "NSW",
        "BN_STATUS": "Registered",
        "Register_Name": "EXAMPLE BUSINESS NAME",
        "_full_text": "'12345678901':1 'busi':4 'cancel':6 'dt':7,11,15 'example':3 'name':5 'nsw':13,18 'nsw12345':17 'reg':9 'register':2,14,19 'renew':12 'stat':16 'status':20 '۲۰۲۰':8 '۲۰۲۳':12",
        "_id": 1
    },
    // ... other records
]


Error Responses
400 Bad Request: If the JSON payload is missing, or if both query and filters are missing.
{"error": "Missing JSON payload"}
```json
{"error": "Missing parameter in JSON payload"}


500 Internal Server Error: If any other exception occurs during processing (e.g., CKAN API error, network issue).
{"exception": "Error: <description of the error>"}


4. Example API Calls
Let's assume the API is running at http://localhost:8080.
a) cURL
Example 1: General query
curl -X POST http://localhost:8080/search \
-H "Content-Type: application/json" \
-d '{
    "query": "COFFEE SHOP",
    "limit": 2
}'


Example 2: Using filters for exact matches
curl -X POST http://localhost:8080/search \
-H "Content-Type: application/json" \
-d '{
    "filters": {
        "BN_STATE_OF_REG": "VIC",
        "BN_STATUS": "Registered"
    },
    "limit": 3
}'


Example 3: Searching a different resource ID
curl -X POST http://localhost:8080/search \
-H "Content-Type: application/json" \
-d '{
    "query": "Technology",
    "resource_id": "another-ckan-resource-id",
    "limit": 10
}'


b) JavaScript (Fetch API)
async function searchCkanApi(payload) {
    const apiUrl = 'http://localhost:8080/search';
    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('API Error:', errorData);
            throw new Error(`HTTP error! status: ${response.status}, message: ${JSON.stringify(errorData)}`);
        }

        const data = await response.json();
        console.log('API Success:', data);
        return data;
    } catch (error) {
        console.error('Fetch Error:', error);
        throw error;
    }
}

// Example Usage:

// 1. General query
searchCkanApi({
    query: "BAKERY",
    limit: 2
});

// 2. Using filters
searchCkanApi({
    filters: {
        "BN_STATE_OF_REG": "QLD"
    },
    limit: 5,
    resource_id: "55ad4b1c-5eeb-44ea-8b29-d410da431be3" // Optional if using default
});

// 3. Query and filters
searchCkanApi({
    query: "Consulting",
    filters: { "BN_STATUS": "Deregistered" },
    limit: 1
});


c) Python (requests library)
First, install the requests library if you haven't already: pip install requests
import requests
import json

API_URL = 'http://localhost:8080/search'

def call_search_api(payload):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
        
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None

# Example Usage:

# 1. General query
payload1 = {
    "query": "CLEANING SERVICE",
    "limit": 2
}
print("\n--- Searching with general query ---")
call_search_api(payload1)

# 2. Using filters
payload2 = {
    "filters": {
        "BN_STATE_OF_REG": "WA",
        "BN_STATUS": "Registered"
    },
    "limit": 3
}
print("\n--- Searching with filters ---")
call_search_api(payload2)

# 3. Searching a different resource ID with a query
payload3 = {
    "query": "health",
    "resource_id": "your-other-resource-id-here", # Replace with an actual resource ID
    "limit": 1
}
print("\n--- Searching different resource ID ---")
# call_search_api(payload3) # Uncomment and replace resource_id to test


5. Notes
The API_TOKEN used by this Flask application is for server-to-server communication with the CKAN instance. It should be kept secure.
The _full_text field in the CKAN response is often used internally by CKAN for its search indexing and might not be directly useful for display purposes.
The actual fields available for filtering (filters parameter) depend on the schema of the specific CKAN resource_id being queried. You

6. Docker 
Config is in Dockerfile using base image python:3.9-slim-buster
Docker image is configured to run on Google cloud run. But not tested.
Run “docker build -t bus-search-app .”  This will create an image and install the app file and all dependencies.
Run “ docker run -p 8080:8080 \       
    -e API_TOKEN="YOUR_API_TOKEN" \
    -e CKAN_INSTANCE_URL="https://data.gov.au/data/" \
    Bus-search-app”
API Token does not appear to be necessary but documentation advises that the site requires it in the header. Dummy placeholder is set as env variable.

Below some example of curl calls once the Docker image is running via terminal

ASIC - Business Names Dataset
https://data.gov.au/dataset/ds-dga-bc515135-4bb6-4d50-957a-3713709a76d3/details?q=business

curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "query": "",
    "filters": {
      "BN_STATUS": "Registered"
    },
    "limit": 10
  }' \
  http://localhost:8080/search

Business and non-business related personal insolvency statistics
https://data.gov.au/dataset/ds-dga-d1151a1d-2f4e-4519-9d6f-103032dae30d/details?q=business

curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "query": "",
    "filters": {
    },
    "resource_id":"41299f46-5c00-41b4-82fc-43edac405b34",
    "limit": 10
  }' \                        
  http://localhost:8080/search
