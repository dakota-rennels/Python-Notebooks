# IMPORTANT! For information on how to use this information, see "Step-by-Step Guide for Running YOLOv4 in Jupyter Notebook" in the same Github repo folder.
# To use, please clone "darknet.zip in this folder.

# !curl https://sdk.cloud.google.com | bash
!gcloud init

## Linking the GCS Bucket to the notebook

from google.auth.transport.requests import Request
from google.oauth2 import id_token
import google.auth

credentials, project = google.auth.default()

# To check if the credentials are working:
auth_req = Request()
id_token.fetch_id_token(auth_req, 'https://www.googleapis.com/auth/cloud-platform')

!gcloud config set project [YOUR GCP PROJECT HERE] # Replace with your GCP project name or ID (should be the same in most cases)

import os
import cv2
import matplotlib.pyplot as plt

# Un-Comment next two lines as needed
#!mkdir -p darknet
#!gsutil -m cp -r gs://darknet_repo/darknet/* ./darknet/

# Making sure the makefile has opencv and gpu enabled
!pip install opencv-python
%cd ..
os.getcwd()
%cd /home/jupyter/darknet/
!python process.py

## Training the Model
!./darknet detector train data/obj.data cfg/yolov4_custom.cfg yolov4.conv.137 -dont_show -map

## Checking for mAP (Mean Average Precision)
%cd /home/jupyter/darknet
!./darknet detector map data/obj.data cfg/yolov4_custom.cfg data/yolov4_custom_last.weights -points 0



# To run the model without training it again: Run cells after this
# Import Libraries here if not running above training code
import os
import cv2
import csv

## Making changes to the custom config file to set it to test mode
%cd cfg
!sed -i 's/batch=64/batch=1/' yolov4_custom.cfg
!sed -i 's/subdivisions=16/subdivisions=1/' yolov4_custom.cfg
%cd ..

#Running the detector on an image for testing

## Testing images
os.chdir('data')
os.getcwd()
!mkdir -p new_2022_data_input
!gsutil -m cp -r gs://input_data/ # Replace with your input data folder path. This is built to use gsutil path for Google Cloud Storage in GCP.
os.getcwd()

## Navigating back to the darknet folder
os.chdir('..')
os.getcwd()

# Directories
input_directory = 'data/new_model_data'
output_directory = 'data/new_model_data_output'

# Ensure output directory exists
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Process images
for image_file in os.listdir(input_directory):
    try:
        img = cv2.imread(os.path.join(input_directory, image_file))
        img = cv2.resize(img, None, fx=0.4, fy=0.4)
        height, width, channels = img.shape

        # Detecting objects
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        # Information to be shown on screen (class, confidence, bounding box coordinates)
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:  # Confidence threshold
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Non-max suppression to avoid multiple boxes for the same object
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        # Draw bounding boxes and labels
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                color = colors[class_ids[i]]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label, (x, y + 30), font, 3, color, 3)

        # Save the processed image
        output_path = os.path.join(output_directory, image_file)
        cv2.imwrite(output_path, img)

    except Exception as e:
        print(f"Error processing {image_file}: {e}")

!ls data/

# Load YOLO model
net = cv2.dnn.readNet("data/yolov4_custom_last.weights", "cfg/yolov4_custom.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

classes = [line.strip() for line in open("data/obj.names")]
os.chdir('..')
os.getcwd()

## This piece of code will result in the images with bounding boxes as well as the final csv
## And generating a separate column for the year of the images

input_directory = 'data/new_2022_data_input'
output_directory = 'data/new_2022_data_output'
csv_file_path = 'data/Final_Output.csv' # Replace 'Final Output' with the desired csv file name

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Class names and corresponding colors for bounding boxes
classes = ["street_sign_example"] # Change with your classes
colors = [(0, 255, 0)] # Change, or add, to customize colors of different classes

# Load the pre-trained model
net = cv2.dnn.readNet("data/training/yolov4_custom_last.weights", "cfg/yolov4_custom.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# CSV header
csv_header = ["ENTER THE NAMES OF YOUR VARIABLES FOR THE CSV FILE/STRUCTURED DATASET"] # Replace with your column names here

# Process each image
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_header)

    for image_file in os.listdir(input_directory):
        img = cv2.imread(os.path.join(input_directory, image_file))
        height, width, channels = img.shape

        # Detect objects
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(output_layers)

        class_ids = []
        confidences = []
        boxes = []
        class_counts = [0, 0, 0, 0]  # Modify for each class. This is an example of 4 classes.

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:  # Confidence threshold
                    center_x, center_y, w, h = map(int, detection[0:4] * [width, height, width, height])
                    x, y = int(center_x - w / 2), int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
                    class_counts[class_id] += 1

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        # Draw bounding boxes and labels
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                color = colors[class_ids[i]]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Save the processed image
        cv2.imwrite(os.path.join(output_directory, image_file), img)

        # Write to CSV
        year = image_file.split('_')[0]  # Extract year
        csv_row = [year, image_file, sum(class_counts)] + class_counts
        writer.writerow(csv_row)
