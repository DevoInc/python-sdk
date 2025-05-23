# Managing Lookups in Devo: Example Notebook with OpenAPI Specification Guidance

This notebook demonstrates how to manage lookups in Devo using the Lookup REST API. It covers listing, creating, updating, deleting, and querying lookups with practical Python code examples.

For general Devo documentation, refer to the [Devo Lookups API documentation](https://docs.devo.com/space/latest/127500334/Working+with+the+Lookups+API).

For the live SWAGGER OpenAPI specification, refer to the [Swagger documentation](https://api-us.devo.com/lookup-api/swagger/).
## Notebook Index

- [1. List All Lookups in a Domain](#1-list-all-lookups-in-a-domain)
- [2. Get Specific Lookup Meta Information](#2-get-specific-lookup-meta-information)
- [3. Create a New Lookup from a CSV File](#3-create-a-new-lookup-from-a-csv-file)
- [4. Simplified Endpoints for Lookup Creation & Updates](#4-simplified-endpoints-for-lookup-creation--updates)
    - [4.1 Create Lookup from a Static Query](#41-create-lookup-from-a-static-query)
    - [4.2 Update Lookup with a Static Query (Simplified Endpoint)](#42-update-lookup-with-a-static-query-simplified-endpoint)
    - [4.3 Create Lookup from a Periodic Query](#43-create-lookup-from-a-periodic-query)
    - [4.4 Create Lookup from a Sliding Window Query](#44-create-lookup-from-a-sliding-window-query)
- [5. Managing Lookup Jobs](#5-managing-lookup-jobs)
    - [5.1 Get Lookup Job UUIDs](#51-get-lookup-job-uuids)
    - [5.2 Query Lookup Job Status](#52-query-lookup-job-status)
- [6. Update Operations](#6-update-operations)
    - [6.1 Update CSV Lookup Data (Full Replace)](#61-update-csv-lookup-data-full-replace)
    - [6.2 Delete Specific Rows from a CSV Lookup](#62-delete-specific-rows-from-a-csv-lookup)
- [7. Delete a Lookup](#7-delete-a-lookup)


```python
import requests, json
import os
from dotenv import load_dotenv
import datetime
import random
import string
import time
```


```python
os.environ.clear()
load_dotenv() # Load environment variables from a .env file if you have one

# --- Configuration ---
# Ensure you have DEVO_API_TOKEN set as an environment variable or replace os.getenv(...) with your actual token.
api_auth_token = os.getenv("DEVO_API_TOKEN", "YOUR_API_TOKEN_HERE") 
domain = "tomaslagom"  # Replace with your actual Devo domain

# Choose the one appropriate for your Devo region (e.g., api-eu.devo.com, api-us.devo.com).
base_url = "https://api-eu.devo.com/lookup-api"

common_headers = {
    "Authorization": f"Bearer {api_auth_token}",
    "Accept": "application/json",
}

# Function to generate unique lookup names for testing to avoid conflicts
def generate_unique_lookup_name(prefix="my_lookup"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}_{timestamp}_{random_suffix}"

# Create example_data directory if it doesn't exist
if not os.path.exists("example_data"):
    os.makedirs("example_data")

# Define the path for the example CSV file
example_csv_path = "example_data/example.csv"

# Content for the example CSV file
example_csv_content = """
KEY,COLOR,HEX
1,Red,d62d20
2,Green,008744
3,Blue,0057e7
4,Yellow,ffa700
5,White,ffffff
""".strip()

# Create the example CSV file
with open(example_csv_path, "w") as f:
    f.write(example_csv_content)

print(f"API Token: {'Loaded' if api_auth_token != 'YOUR_API_TOKEN_HERE' else 'Not Loaded - Please configure!'}")
print(f"Domain: {domain}")
print(f"Base URL: {base_url}")
print(f"Example CSV created at: {example_csv_path}")

# Variables to store names of lookups created, to be used in later cells for update/delete
created_csv_lookup_name = None
created_static_query_lookup_name = None
created_periodic_lookup_name = None
created_sliding_lookup_name = None
```

## 1. List All Lookups in a Domain

This operation retrieves a list of lookups within the specified domain.

[listLookups Swagger documentation](https://api-us.devo.com/lookup-api/swagger/#/default/listLookups).


```python
print("--- Listing Lookups ---")
list_lookups_url = f"{base_url}/lookup/{domain}"

response = requests.get(list_lookups_url, headers=common_headers)
print(f"Status code: {response.status_code}")

lookups_data = response.json().get('lookups', [])
print(f"Found {len(lookups_data)} lookups.")
```

## 2. Get Specific Lookup Meta Information

This operation retrieves detailed meta information for a specific lookup.

[getLookupMetaInfo Swagger documentation](https://api-us.devo.com/lookup-api/swagger/#/default/getLookupMetaInfo).


```python
print("\n--- Getting Specific Lookup Meta Information ---")
# You can get a list of lookups from the previous step.
lookup_to_get = "Test_Lookup_Csv" # CHANGE THIS to an existing lookup name in your domain
get_lookup_url = f"{base_url}/lookup/{domain}/{lookup_to_get}"

response = requests.get(get_lookup_url, headers=common_headers)
print(f"Status code for getting '{lookup_to_get}': {response.status_code}")
print("Response JSON:", response.json())
```

## 3. Create a New Lookup from a CSV File

This operation creates a new lookup by uploading a CSV file and its configuration.

[createCsvLookup Swagger documentation](https://api-us.devo.com/lookup-api/swagger/#/default/createCsvLookup)


```python
print("\n--- Creating a New Lookup from CSV ---")
created_csv_lookup_name = generate_unique_lookup_name("my_csv_colors_lookup")
csv_file_path = example_csv_path # Using the CSV file created in the setup cell

print(f"Attempting to create lookup: {created_csv_lookup_name}")
print(f"Using CSV file: {csv_file_path}")

# Define the 'deploy-config' JSON. 
deploy_config_dict = {
    "columns": [
        {"name": "KEY", "type": "INT8"},    # 'name' should match CSV header, 'type' is Devo data type
        {"name": "COLOR", "type": "STRING"},
        {"name": "HEX", "type": "STRING"}
    ],
    "hasHeader": True,  # Set to True if your CSV file's first row is a header
    "key": { # Defines the primary key for the lookup
        "type": "column",
        "column": "KEY"  # Name of the column to be used as key
    }
    # "skipEmptyLines": True, 
    # "visibility": {"type": "creator-only"} 
}
deploy_config_json_string = json.dumps(deploy_config_dict)

create_csv_lookup_url = f"{base_url}/lookup/{domain}/{created_csv_lookup_name}/deploy-csv"

# Specific headers for file upload (Authorization only, Content-Type is set by requests for multipart)
upload_headers = {"Authorization": f"Bearer {api_auth_token}"}

file = {
    "deploy-config": (None, deploy_config_json_string, "application/json"),
    "csv": (os.path.basename(csv_file_path), open(csv_file_path, "rb"), "text/csv")
}
response = requests.post(create_csv_lookup_url, headers=upload_headers, files=file)

print(f"Status code for creating '{created_csv_lookup_name}': {response.status_code}")
print("Response JSON:", response.json())
print(f"Lookup '{created_csv_lookup_name}' creation request submitted successfully.")
```

## 4. Simplified Endpoints for Lookup Creation & Updates

The Devo Lookup API provides simplified endpoints for creating or updating lookups based on different source types (static query, periodic query, sliding window query). These typically involve sending a JSON payload directly.

### 4.1 Create Lookup from a Static Query

Creates a lookup whose data is the result of a one-time execution of a Devo query.

[createStaticQueryLookup Swagger documentation](https://api-us.devo.com/lookup-api/swagger/#/default/createStaticQueryLookup)


```python
print("\n--- Creating Lookup from Static Query ---")
created_static_query_lookup_name = generate_unique_lookup_name("my_static_q_lookup")

# Ensure the query selects columns that you will define in your 'key' and potentially use.
devo_query_for_lookup = "from siem.logtrust.web.navigation select eventdate, userid, domain where now() - 1h < eventdate limit 10"

# Construct the payload based on the 'DeployStaticQuery' schema in OpenAPI.
static_query_payload = {
    "query": devo_query_for_lookup,
    "key": { # Defines the primary key for the lookup
        "type": "column", # or 'first-column', etc.
        "column": "userid" # Must be a column selected in your query
    }
    # Optional fields from DeployStaticQuery schema:
    # "visibility": {"type": "creator-only"},
    # "keepHistory": False,
    # "columnTimeReference": None, 
    # "append": False 
}

create_static_query_url = f"{base_url}/lookup/{domain}/{created_static_query_lookup_name}/deploy-static-query"
request_headers = {**common_headers, "Content-Type": "application/json"}

response = requests.post(create_static_query_url, headers=request_headers, data=json.dumps(static_query_payload))

print(f"Status code for creating '{created_static_query_lookup_name}': {response.status_code}")
```

### 4.2 Update Lookup with a Static Query (Simplified Endpoint)

Updates an existing lookup to be sourced from a new static query using a simplified `PUT` endpoint. This typically replaces the lookup's content based on the new query.

[putStaticQueryLookup Swagger documentation](https://api-us.devo.com/lookup-api/swagger/#/default/putStaticQueryLookup)


```python
print("\n--- Updating Lookup with Static Query (Simplified Endpoint) ---")
# Use the name of the static query lookup created in the previous step.
lookup_to_update_name_static = created_static_query_lookup_name 

print(f"Attempting to update lookup: {lookup_to_update_name_static}")
updated_devo_query = "from siem.logtrust.web.activity select eventdate, clientIpAddress, statusCode where now() - 30m < eventdate limit 5"

# Payload based on 'DeployStaticQuery' schema
update_static_query_payload = {
    "query": updated_devo_query,
    "key": {
        "type": "column",
        "column": "clientIpAddress" 
    }
}

update_static_query_url = f"{base_url}/lookup/{domain}/{lookup_to_update_name_static}/deploy-static-query"
request_headers = {**common_headers, "Content-Type": "application/json"}

response = requests.put(update_static_query_url, headers=request_headers, data=json.dumps(update_static_query_payload))

print(f"Status code for updating '{lookup_to_update_name_static}': {response.status_code}")
```

### 4.3 Create Lookup from a Periodic Query

Creates a lookup that is updated periodically by re-executing a Devo query.

[createPeriodicQueryLookup Swagger documentation](https://api-us.devo.com/lookup-api/swagger/#/default/createPeriodicQueryLookup)


```python
print("\n--- Creating Lookup from Periodic Query ---")
created_periodic_lookup_name = generate_unique_lookup_name("my_periodic_lookup")

periodic_devo_query = "from siem.logtrust.web.navigation select eventdate, userid group every 5m by userid"

# Payload based on 'DeployPeriodicQuery' schema
periodic_query_payload = {
    "query": periodic_devo_query,
    "key": {
        "type": "column",
        "column": "userid" # Adjust if your query's key structure is different
    },
    # "refreshPeriod": "5m", # How often the query reruns. Defaults to grouping period of the query in case it is a grouping query, or 5 minutes if not. (e.g., "5m", "1h")
    # "startDate": "2025-05-12T00:00:00.00Z", # Defaults to the time of the request.Can either be an ISO-8601 datetime string or a number of milliseconds from EPOCH
    # "keepHistory": True      # default: false. If enabled, Lookup Manager will store all historic data in the lookup, enabling historic search.
}

create_periodic_url = f"{base_url}/lookup/{domain}/{created_periodic_lookup_name}/deploy-periodic-query"
request_headers = {**common_headers, "Content-Type": "application/json"}

response = requests.post(create_periodic_url, headers=request_headers, data=json.dumps(periodic_query_payload))
print(f"Status code for creating '{created_periodic_lookup_name}': {response.status_code}")
```

### 4.4 Create Lookup from a Sliding Window Query

Creates a lookup based on a query that operates over a sliding time window. A sliding window lookup in Devo is a type of lookup table that is dynamically updated based on a query that runs over a defined, moving time window. ⏳ It's useful for keeping track of recent activity or maintaining aggregated data over a specific recent period.


[createSlidingWindowQuery Swagger documentation](https://api-us.devo.com/lookup-api/swagger/#/default/createSlidingWindowQuery)


```python
print("\n--- Creating Lookup from Sliding Window Query ---")
created_sliding_lookup_name = generate_unique_lookup_name("my_sliding_lookup")

sliding_devo_query = "from siem.logtrust.web.activity select domain, responseTime group every 1m by domain"

# The field for window size is 'windowSize' in the provided spec.
sliding_query_payload = {
    "query": sliding_devo_query,
    "key": {
        "type": "column",
        "column": "domain"
    },
    "windowSize": "1h",     # Total window size (e.g., "1d", "6h")
    "refreshPeriod": "10m", # How often the window slides/query refreshes (e.g., "10m", "1m")
    # "startDate": "2025-05-12T00:00:00.00Z", # Optional start date
    # "visibility": ..., "keepHistory": ..., "columnTimeReference": ...
}

create_sliding_url = f"{base_url}/lookup/{domain}/{created_sliding_lookup_name}/deploy-sliding-window-query"
request_headers = {**common_headers, "Content-Type": "application/json"}

response = requests.post(create_sliding_url, headers=request_headers, data=json.dumps(sliding_query_payload))
print(f"Status code for creating '{created_sliding_lookup_name}': {response.status_code}")
```

## 5. Managing Lookup Jobs

After creating or updating a lookup, especially query-based ones, Devo processes them as jobs. You can query the status of these jobs.

### 5.1 Get Lookup Job UUIDs

Retrieves a list of job UUIDs associated with a given lookup.

[getLookupJobsUUIDs Swagger documentation](https://api-us.devo.com/lookup-api/swagger/#/default/getLookupJobsUUIDs)


```python
print("\n--- Getting Lookup Job UUIDs ---")
lookup_name_for_jobs = created_periodic_lookup_name # Using the periodic lookup as an example

get_jobs_url = f"{base_url}/lookup/{domain}/{lookup_name_for_jobs}/job"
response = requests.get(get_jobs_url, headers=common_headers)

if response.ok:
    # Response structure is 'LookupJobListResponse' in OpenAPI
    job_data = response.json()
    print("Response JSON:", job_data)
    if job_data.get("jobs") and len(job_data.get("jobs")) > 0:
        first_job_id = job_data["jobs"][0]
        print(f"First job ID: {first_job_id}")
    else:
        print("No jobs found for this lookup yet or an error occurred retrieving them.")
```

### 5.2 Query Lookup Job Status

Retrieves the status history for a specific lookup job ID.

[queryLookupJobStatus Swagger documentation](https://api-us.devo.com/lookup-api/swagger/#/default/queryLookupJobStatus)


```python
print("\n--- Querying Lookup Job Status ---")
lookup_name_for_job_status = lookup_name_for_jobs # Using a lookup name and a job ID obtained from the previous step.

job_id_to_query = first_job_id # From the output of the cell above

if lookup_name_for_job_status and job_id_to_query:
    print(f"Attempting to get status for job '{job_id_to_query}' of lookup '{lookup_name_for_job_status}'")
    get_job_status_url = f"{base_url}/lookup/{domain}/{lookup_name_for_job_status}/job/{job_id_to_query}"
    try:
        response = requests.get(get_job_status_url, headers=common_headers)
        print(f"Status code for job '{job_id_to_query}': {response.status_code}")
        if response.ok:
            # Response structure is 'LookupJobStatusListResponse' in OpenAPI
            print("Response JSON:", response.json())
        else:
            print("Error Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
else:
    print("Skipping job status query. Ensure lookup name and job ID were retrieved successfully in the previous step.")
```

## 6. Update Operations

The API supports updating existing lookups. This can involve changing their configuration or data. `PUT` requests are generally used for updates.

### 6.1 Update CSV Lookup Data (Full Replace)

This example demonstrates how to update an existing CSV lookup by uploading a new CSV file.

[putCsvLookup Swagger documentation](https://api-us.devo.com/lookup-api/swagger/#/default/putCsvLookup)


```python
print("\n--- Updating CSV Lookup (Full Data Replace Example) ---")
lookup_to_update_csv = created_csv_lookup_name # Using the CSV lookup created in section 3

print(f"Attempting to update CSV lookup: {lookup_to_update_csv}")
# Create a new CSV content for update
updated_csv_content = """
KEY,COLOR,HEX,NEW_INFO
1,Dark Red,aa0000,UpdatedRow1
6,Orange,ffa500,NewRow6
""".strip()
    
updated_csv_path = "example_data/updated_example.csv"
with open(updated_csv_path, "w") as f:
    f.write(updated_csv_content)
print(f"Created updated CSV data at: {updated_csv_path}")

# If columns change, this config MUST reflect the new structure.
update_deploy_config_dict = {
        "columns": [
            {"name": "KEY", "type": "INT8"},
            {"name": "COLOR", "type": "STRING"},
            {"name": "HEX", "type": "STRING"},
            {"name": "NEW_INFO", "type": "STRING"} # New column
        ],
        "hasHeader": True,
        "key": {"type": "column", "column": "KEY"},
    }
update_deploy_config_json_string = json.dumps(update_deploy_config_dict)

update_csv_lookup_url = f"{base_url}/lookup/{domain}/{lookup_to_update_csv}/deploy-csv"
upload_headers = {"Authorization": f"Bearer {api_auth_token}"}

files_to_send = {
    "deploy-config": (None, update_deploy_config_json_string, "application/json"),
    "csv": (os.path.basename(updated_csv_path), open(updated_csv_path, "rb"), "text/csv")
}
response = requests.put(update_csv_lookup_url, headers=upload_headers, files=files_to_send)
    

print(f"Status code for updating CSV lookup '{lookup_to_update_csv}': {response.status_code}")
print("Response JSON:", response.json())
```

### 6.2 Delete Specific Rows from a CSV Lookup

To delete specific rows from an existing CSV lookup, you upload a new CSV file containing only the keys of the rows to be deleted. The `deploy-config` must specify `contribution: {"type": "del"}`.

[putCsvLookup Swagger documentation](https://api-us.devo.com/lookup-api/swagger/#/default/putCsvLookup)


```python
print("\n--- Deleting Specific Rows from CSV Lookup ---")
lookup_to_modify_rows = created_csv_lookup_name # Using the CSV lookup from section 3

print(f"Attempting to delete rows from CSV lookup: {lookup_to_modify_rows}")

# Create a CSV file with keys of rows to delete. Let's delete KEY=2.
# This CSV must have the header for the key column.
keys_to_delete_content = """
KEY,COLOR,HEX
2,Green,008744
4,Yellow,ffa700
""".strip()
    
keys_to_delete_csv_path = "example_data/keys_to_delete.csv"
with open(keys_to_delete_csv_path, "w") as f:
    f.write(keys_to_delete_content)
print(f"Created CSV with keys to delete at: {keys_to_delete_csv_path}")

# Define 'deploy-config' for row deletion.
delete_rows_deploy_config_dict = {
    "columns": [
        {"name": "KEY", "type": "INT8"},
        {"name": "COLOR", "type": "STRING"},
        {"name": "HEX", "type": "STRING"}
    ],
    "hasHeader": True,
    "key": {"type": "column", "column": "KEY"}, # Must match the lookup's actual key
    "append": True, # needed to Keep the other rows
    "contribution": {"type": "del"} # This is crucial for deleting rows
}
delete_rows_deploy_config_json_string = json.dumps(delete_rows_deploy_config_dict)

delete_rows_url = f"{base_url}/lookup/{domain}/{lookup_to_modify_rows}/deploy-csv"
upload_headers = {"Authorization": f"Bearer {api_auth_token}"}

with open(keys_to_delete_csv_path, "rb") as delete_keys_file_object:
    files_to_send = {
        "deploy-config": (None, delete_rows_deploy_config_json_string, "application/json"),
        "csv": (os.path.basename(keys_to_delete_csv_path), delete_keys_file_object, "text/csv")
    }
    response = requests.put(delete_rows_url, headers=upload_headers, files=files_to_send)

print(f"Status code for deleting rows from '{lookup_to_modify_rows}': {response.status_code}")
print("Response JSON:", response.json())
```

## 7. Delete a Lookup

This operation permanently deletes a lookup from the domain.

[deleteLookup Swagger documentation](https://api-us.devo.com/lookup-api/swagger/#/default/deleteLookup)


```python
print("\n--- Deleting a Lookup ---")
# IMPORTANT: This will delete the lookup. We'll try to delete the CSV lookup created earlier in this notebook.
lookup_to_delete = created_csv_lookup_name 

print(f"Attempting to delete lookup: {lookup_to_delete}")
delete_lookup_url = f"{base_url}/lookup/{domain}/{lookup_to_delete}"

    

response = requests.delete(delete_lookup_url, headers=common_headers)
print(f"Status code for deleting '{lookup_to_delete}': {response.status_code}")

# Response structure is 'LookupDeletionResponse' in OpenAPI
print("Response JSON:", response.json())
print(f"Lookup '{lookup_to_delete}' deletion request submitted successfully.")
if created_csv_lookup_name == lookup_to_delete:
    created_csv_lookup_name = None # Clear the variable as it's deleted
```
