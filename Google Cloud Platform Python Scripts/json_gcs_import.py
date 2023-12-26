import os
from google.cloud import storage
import pandas as pd

# Replace with the path to your JSON file
json_file_path = 'JSON FILE PATH'

# Replace with your GCS bucket and JSON file path
bucket_name = 'BUCKET NAME'
json_blob_name = 'JSON FILE NAME'
local_file_path = 'LOCAL DESTINATION PATH'

# Initialize a GCS client
client = storage.Client()

# Get the GCS bucket
bucket = client.get_bucket(bucket_name)

# Get the blob file from the bucket
blob = bucket.blob(json_blob_name)

# Download the JSON file to the local folder
blob.download_to_filename(local_file_path)

print(f'JSON file copied to {local_file_path}')
