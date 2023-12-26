from google.cloud import storage
import zipfile
import os

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def unzip_file(zip_path, extract_path):
    """Unzips a file."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    print(f"Extracted {zip_path} to {extract_path}")

def main(bucket_name, zip_blob_name):
    local_zip_file = "temp.zip"
    local_extract_path = "temp_extracted"

    # Download the zip file from GCS
    download_blob(bucket_name, zip_blob_name, local_zip_file)

    # Unzip the file locally
    unzip_file(local_zip_file, local_extract_path)

    # Upload the unzipped files back to GCS
    for root, dirs, files in os.walk(local_extract_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            remote_file_path = os.path.join(zip_blob_name.replace(".zip", ""), os.path.relpath(local_file_path, local_extract_path))
            upload_blob(bucket_name, local_file_path, remote_file_path)

    # Clean up local files (optional)
    os.remove(local_zip_file)
    for root, dirs, files in os.walk(local_extract_path, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))

# Usage
bucket_name = 'ENTER GCP BUCKET NAME HERE'  # Just the bucket name, no 'gs://' prefix
zip_blob_name = 'ENTER FILE PATH WITHIN BUCKET HERE'  # Path to the file within the bucket
main(bucket_name, zip_blob_name)
