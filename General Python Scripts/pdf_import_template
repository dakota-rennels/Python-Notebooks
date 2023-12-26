import os
from google.cloud import storage

# GCS bucket and object details
bucket_name = "BUCKET NAME"
object_name = "OBJECT PATH"

# Local file path to save the PDF
local_file_path = "LOCAL PATH DESTINATION"

# Initialize the GCS client
storage_client = storage.Client()

# Get the GCS bucket and object
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(object_name)

# Download the PDF from GCS and save it locally
blob.download_to_filename(local_file_path)

print(f"PDF saved locally at: {local_file_path}")
