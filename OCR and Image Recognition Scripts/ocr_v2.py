### IMPORTANT! This OCR code utilizes DocumentAI in GCP for the actual OCR model. HOWEVER, you can sub the initial processing work with a TessaractOCR model and the remaining code will work.
# This OCR code was used to extract latitude, longitude, and collection date from an image passed through and build a collective dataset. Depending on your OCR model, you can easily swap out these variables for your model's variables.

# Copy and Paste each line into new code line without comments to install into Kernel
#pip install google-cloud-documentai
#pip install google-cloud-storage

# Import Libraries
from google.cloud import documentai_v1 as documentai
from google.cloud import storage
from google.oauth2 import service_account
import os
import pandas as pd
import re
import tempfile
from google.api_core import retry
from google.api_core import exceptions

# Replace with your actual details
project_id = 'YOUR GCP PROJECT ID'
location = 'us'  # Format is 'us'
processor_id = 'YOUR DOCUMENTAI PROCESSOR ID'
service_account_file = 'YOUR GCP SERVICE ACCOUNT JSON KEY.json'

# Authenticate to the API
credentials = service_account.Credentials.from_service_account_file(service_account_file)
client = documentai.DocumentProcessorServiceClient(credentials=credentials)

# Apply the retry decorator to the process_document function
@retry.Retry(predicate=retry.if_exception_type(exceptions.InternalServerError),
             initial=1, maximum=10, multiplier=2)

def process_document(file_path):
    with open(file_path, 'rb') as image:
        image_content = image.read()

    # Configure the process request
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
    document = documentai.types.Document(content=image_content, mime_type='image/jpeg')
    request = documentai.ProcessRequest(name=name, inline_document=document)

    # Increase the timeout for processing the document
    timeout = 900  # Timeout in seconds (e.g., 600 seconds = 10 minutes)

    # Process the document with increased timeout
    result = client.process_document(request=request, timeout=timeout)

    # Extract the text
    document = result.document
    text = document.text

    return text

# Function to parse text banner
def parse_text_banner(text):
    # Regular expressions to find the patterns in the text
    lat_pattern = r'LAT: (\S+)'
    lon_pattern = r'LON: (\S+)'
    colldate_pattern = r'COLLDATE: (\S+)'  # Adjust this regex based on your date format

    # Search for the patterns and extract the values
    lat_match = re.search(lat_pattern, text)
    lon_match = re.search(lon_pattern, text)
    colldate_match = re.search(colldate_pattern, text)

    # Extract values using a group; group(0) is the full match, group(1) is the first capture group
    lat = lat_match.group(1) if lat_match else None
    lon = lon_match.group(1) if lon_match else None
    colldate = colldate_match.group(1) if colldate_match else None

    return lat, lon, colldate

# Initialize the Google Cloud Storage client
storage_client = storage.Client(credentials=credentials)

# Name of your GCS bucket
bucket_name = 'YOUR BUCKET NAME'

# Folder within the bucket
desired_folder = 'YOUR FOLDER PATH'

# Get the bucket object
bucket = storage_client.get_bucket(bucket_name)

# List all the blobs in the bucket
all_blobs = bucket.list_blobs()

# Filter blobs to include only those in the desired folder
filtered_blobs = [blob for blob in all_blobs if blob.name.startswith(desired_folder)]

# DataFrame to store results
df = pd.DataFrame(columns=["FileName", "LAT", "LON", "COLLDATE"])
data_batch = []  # Temporary storage for the data

# Process each image and extract data
for index, blob in enumerate(filtered_blobs):
    # Skip blobs with 'unpacked_data' in their name
    if 'unpacked_data' in blob.name.lower():
        continue

    if blob.name.lower().endswith('.jpg'):
        # Create a temporary file and ensure it gets closed properly
        file_descriptor, temp_local_filename = tempfile.mkstemp()
        try:
            blob.download_to_filename(temp_local_filename)
            os.close(file_descriptor)  # Close the file descriptor
                       
            # Process the downloaded image
            text = process_document(temp_local_filename)
            ctlsect, chain, lat, lon, colldate = parse_text_banner(text)
            
            # Collect data
            data_batch.append({
                "FileName": blob.name,
                "LAT": lat,
                "LON": lon,
                "COLLDATE": colldate
            })
        finally:
            os.remove(temp_local_filename)  # Delete the temporary file

        # Save progress every 50 images
        if (index + 1) % 50 == 0:
            df_batch = pd.DataFrame(data_batch)
            df = pd.concat([df, df_batch], ignore_index=True)
            df.to_csv('output_batch.csv', index=False)
            data_batch = []  # Reset the temporary storage

# Add any remaining data to the DataFrame and save
if data_batch:
    df_batch = pd.DataFrame(data_batch)
    df = pd.concat([df, df_batch], ignore_index=True)
    df.to_csv('output_batch.csv', index=False)

# Save the results
df.to_csv('final_extracted_ocr_data.csv', index=False)
