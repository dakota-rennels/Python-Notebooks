### IMPORTANT! This code is still being developed to perform more dynamically without hard coding BQ SQL Queries
# This code is built to be added as a Webhook to communicate with DialogFlow CX.
# Add as a Cloud Function in GCP and assign Python 3.9 or later.

# Import Libraries
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import logging
import json

# Create BigQuery client
def create_bigquery_client():
    credentials = service_account.Credentials.from_service_account_file(
        'service_account_json.json')
    return bigquery.Client(credentials=credentials)

# Logging for operation tracking
logging.basicConfig(level=logging.INFO)
logging.info("Query executed successfully")

# Function to query data from BigQuery
def query_bigquery(client, query):
    query_job = client.query(query)
    return query_job.result().to_dataframe()

# Descriptive statistics function
def descriptive_statistics(dataframe):
    return dataframe.describe()

# Top 10 Function
def top_10_records(dataframe, column_name):
    return dataframe.sort_values(by=column_name, ascending=False).head(10)

# Max values Function
def max_value(dataframe, column):
    return dataframe[column].max()

# Average Values Function
def average_value(dataframe, column):
    return dataframe[column].mean()

# Value Counts Function
def value_counts(dataframe, column):
    return dataframe[column].value_counts(sort=True, ascending=False)

# Count Nulls Function
def count_nulls(dataframe, column):
    return dataframe[column].isnull().sum()

# Count Zeros Function
def count_zeros(dataframe, column):
    return (dataframe[column] == 0).sum()

# Count Nulls and Zeros Function
def count_nulls_and_zeros(dataframe, column):
    null_count = dataframe[column].isnull().sum()
    zero_count = (dataframe[column] == 0).sum()
    return null_count + zero_count

# Dictionary of queries for each dataset
try:
    queries = {
    'ENTER SQL OR BIGQUERY SQL STATEMENT HERE'
    # ... Add other queries for each dataset
}
except Exception as e:
    print(f"An error occurred: {e}")
    # Handle the error or re-raise

# DialogFlow CX Handling Function (Critical form Ingestion)
def handle_dialogflow_request(request_payload):
    client = create_bigquery_client()
    payload = json.loads(request_payload)

    intent_name = payload.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = payload.get("queryResult", {}).get("parameters", {})

    if intent_name in queries:
        try:
            query = queries[intent_name]
            data = query_bigquery(client, query)

            request_type = parameters.get("requestType")
            column_name = parameters.get("columnName")

            if request_type == 'top_10' and column_name:
                result = top_10_records(data, column_name).to_json()
            elif request_type in ['max_value', 'average'] and column_name:
                # Processing for max_value and average
                value = (float(max_value(data, column_name)) if request_type == 'max_value'
                         else float(average_value(data, column_name)))
                result = json.dumps({f"{request_type}_{column_name}": value})
            elif request_type == 'count_nulls' and column_name:
                # Processing for count_nulls
                value = int(count_nulls_and_zeros(data, column_name))
                result = json.dumps({f"count_nulls_{column_name}": value})
            elif request_type == 'count_zeros' and column_name:
                # Processing for count_zeros
                value = int(count_zeros(data, column_name))
                result = json.dumps({f"count_zeros_{column_name}": value})
            elif request_type == 'count_nulls_and_zeros' and column_name:
                # Processing for count_nulls
                value = int(count_nulls_and_zeros(data, column_name))
                result = json.dumps({f"count_nulls_and_zeros_{column_name}": value})
            else:
                result = descriptive_statistics(data).to_json()

            return result
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return json.dumps({"error": str(e)})
    else:
        return json.dumps({"error": "No data available for this query."})
