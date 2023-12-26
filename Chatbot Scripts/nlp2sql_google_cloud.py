# Un-Comment to force install google auth library
#pip install --force-reinstall --no-deps google-auth==2.23.0

#!pip install google-cloud-aiplatform --upgrade

# Install Necessary Libraries
import os
from google.cloud import aiplatform
from google.cloud import bigquery

# Assign Service Account
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'ENTER JSON KEY FOR SERVICE ACCOUNT IN GCP'

# Initialize the AI Platform model service client
models_client = aiplatform.gapic.ModelServiceClient()

# Initialize the BigQuery client
bigquery_client = bigquery.Client()

## Deploying Endpoint to Project
# There is a dedicated, custom Docker container **us-docker.pkg.dev/vertex-ai-restricted/cair/prediction/text2sql_bq** which can be deployed to your project directly.
# This is a one time action as long as there is a deployed endpoint.

# Specify the following parameters for the endpoint deployment
MODEL_DISPLAY_NAME = "text2sql-model"
IMAGE_URI = "us-docker.pkg.dev/vertex-ai-restricted/cair/prediction/text2sql_bq"
LOCATION = "ENTER YOUR GCP LOCATION BASED ON YOUR CURRENT REGION"

PROJECT_ID="ENTER YOUR GCP PROJECT ID" 
MACHINE_TYPE = "n1-standard-4" # Either leave this as default or specify the machine type you desire.
# This deployment needs a service account that the deployed model's container runs as.
# Please give "BigQuery Data Viewer", "Vertex AI Service Agent" and "Vertex AI User" permissions in IAM for the service account used to run the Text2SQL pipeline.
SERVICE_ACCOUNT = "ENTER YOUR GCP SERVICE ACCOUNT NAME THAT HAS BEEN ASSIGNED THE ABOVE PERMISSIONS"


def upload_model():
  model = aiplatform.Model.upload(
      display_name=MODEL_DISPLAY_NAME,
      serving_container_image_uri=IMAGE_URI,
  )
  return model

def deploy_model_to_endpoint(deployed_model):
  endpoint = deployed_model.deploy(
    machine_type=MACHINE_TYPE, service_account=SERVICE_ACCOUNT
  )
  return endpoint

def undeploy_model_and_delete_endpoint(endpoint_id):
  endpoint = aiplatform.Endpoint(
    endpoint_name=f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}")

  endpoint.undeploy_all()
  endpoint.delete()

aiplatform.init(project=PROJECT_ID, location=LOCATION)

# Endpoint deployment
model = upload_model()
endpoint = deploy_model_to_endpoint(model)
print(f'Endpoint id is: {endpoint.name}')

# Running Text2SQL

# Variables added if a user has already deployed the endpoint
LOCATION = "YOUR REGION OF YOUR DEPLOYED ENDPOINT (REGION OF PREVIOUS SECTION)"
PROJECT_ID="YOUR GCP PROJECT ID"

# Once you have deployed the endpoint (check previous section) with the Text2SQL server, specify the following parameters. 
# For more information, check the [endpoint documentation](https://cloud.google.com/vertex-ai/docs/predictions/using-private-endpoints). Endpoint deployment might take a few minutes to run.
ENDPOINT_ID = "1234567891234567890" #REPLACE WITH YOUR ENDPOINT ID

# Now build the Text2SQL endpoint request which will called to convert the natural language english question into a BQ SQL query.
# You should specify the "NL QUESTION" parameter which contains the natural language question and can also contain extra information that might be helpful for the model (e.g. "Ignore null values"). 
# Questions should not contain any instructions related to modifying the table such as "delete", "change", "drop", "remove", "update" and only contain language related to querying the data such as "What" and "how many".
NL_QUESTION = "Get total number of people from state of WA grouped by name and state, limit results by 10 and sort by highest to lowest." # Replace with your own question.
BQ_DATASET = "bigquery-public-data.usa_names" # Replace with your BQ dataset

## Important!
# When the BQ dataset is too large, the underlying prompt might be larger than the supported token limit of the LLM.
# Therefore provide a way to provide filters that limit tables/columns from the schema that the model will have access to.
# For more information on LLM token limits, check [here](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models#foundation_models).

# If the Text2SQL endpoint requests fails with an error similar to `[ORIGINAL ERROR] generic::invalid_argument: The model supports up to 8192 input tokens, but received 2100001 tokens.`, specify the parameters below.

# The following are optional parameters but help mitigate the issue with the token limit:

# List of strings of BQ table names denoting subset from the BQ dataset that should be considered. Use the full table name, e.g. **["bigquery-public-data.london_bicycles.cycle_stations", ...]**.
BQ_TABLES_FILTER = [] 
# Optional dict of { table name strings : list of columns names } denoting columns to be considered for each table. The model will only see the table bigquery-public-data.london_bicycles.cycle_stations and think that it only has 3 columns:  "id", "name", "install_date". Should only be used when execution_mode="manual". E.g. **{ "bigquery-public-data.london_bicycles.cycle_stations": ["id", "name", "install_date"] }**
BQ_COLUMNS_FILTER = {} 

## [Optional] Advanced Features
# Setting `NUM_SELF_CORRECT_ATTEMPTS` to a value greater than 0 enables the self-correction module which queries the LLM in case any errors happen in the generated query.
# We've seen that this consistently improves performance of the generated SQL with the additional cost of latency. Try setting this to 1 to see if this improves SQL quality.
NUM_SELF_CORRECT_ATTEMPTS = 0 # Replace with a desired number of attempts. EDIT: I have seen much success using 2.

# Setting `EXECUTION_MODE` to "auto" enables an automatic selection module that tries to automatically select relevant tables/columns for the input question.
# Currently, under-the-hood, Text2SQL V1 considers all tables/columns as potentially relevant to the input question. 
# This can result into incorrectly generated SQL if the BQ dataset has multiple tables (>3 and/or multiple columns (>10).
# Note, that this also increases latency so prefer using `BQ_TABLES_FILTER` and `BQ_COLUMNS_FILTER` instead if that is a possibility
EXECUTION_MODE = 'manual' # Supported values: 'auto' and 'manual'.

### Helper: building the request

# You can control the number of samples made to the LLM which improves the chance of the generated sql query to be correct.
# A lower value translated to lower latency but worse performance. Additionaly, the request cost will be proportional to `NB_SAMPLES`.
NB_SAMPLES = 8 
# The temperature parameter controls the degree of diversity of the generated SQL outputs. 
# Since Text2SQL samples multiple times from the LLM, a `temperature > 0.5` is essential to generate a diverse set of candidate SQL to select from.
# For more information on temperature (and other model parameters), check [here](https://developers.generativeai.google/guide/concepts#model_parameters).
TEMPERATURE = 0.8

def build_request(bq_tables_filter = None, bq_columns_filter = None):
  """Creates a single endpoint request."""

  example_input = [
    {
      "text": NL_QUESTION,
      "bq_dataset": BQ_DATASET,
      "project_id": PROJECT_ID,
      "execution_mode": EXECUTION_MODE,
    }]
  if bq_tables_filter:
    example_input[0]["bq_tables_filter"] = bq_tables_filter
  if bq_columns_filter:
    example_input[0]["bq_columns_filter"] = bq_columns_filter

  params = {
    "temperature": TEMPERATURE,
    "nb_samples": NB_SAMPLES,
    "nb_self_correct_attempts": NUM_SELF_CORRECT_ATTEMPTS,
  }

  return example_input, params

### Call Text2SQL endpoint
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# build request
example_input, params = build_request(bq_columns_filter=BQ_COLUMNS_FILTER, bq_tables_filter=BQ_TABLES_FILTER)

# Query via Endpoint directly
endpoint = aiplatform.Endpoint(
    endpoint_name=f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}")

# The endpoint request
response = endpoint.predict(instances=example_input, parameters=params)

# response.predictions[0] is a dictionary:
# {
#  "status" "result" or "exception",
#  "sql_query" : "Generated SQL query string"
# }
response.predictions[0]

sql_query = response.predictions[0]['sql_query']
print("Generated SQL query:", sql_query)

#[Optional] Execute generated SQL query on BQ data
client = bigquery.Client(project=PROJECT_ID)
df_res = client.query(sql_query).to_dataframe()
df_res

## [Optional] Cleaning up
# When you are done, undeploy and delete the endpoint. Uncomment the following code.
# undeploy_model_and_delete_endpoint(ENDPOINT_ID)
