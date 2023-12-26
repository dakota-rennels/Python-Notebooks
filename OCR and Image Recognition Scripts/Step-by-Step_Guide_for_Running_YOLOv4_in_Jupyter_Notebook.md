Step-by-Step Guide for Running YOLOv4 in Jupyter Notebook
Link to the Python code: https://github.com/dakota-rennels/Python-Notebooks/blob/main/OCR%20and%20Image%20Recognition%20Scripts/yolo4_image_recognition.py

Part I: Running the Pretrained Model
1.	Create Input Folder:
•	In the Jupyter Notebook's "File Browser" section, navigate to the darknet -> data folder.
•	Create a new folder named NewImages_input (or another name of your choice).

2.	Upload Images:
•	Upload the images you want to process into the NewImages_input folder.
•	Alternatively, run the provided cell in the notebook to create new_2022_data_input and copy images from the specified GCS Bucket.

3.	Prepare for Model Execution:
•	Ensure you're in the darknet directory, not inside the data directory.
•	Confirm that input and output directories are correctly defined in the notebook.
•	Optionally, you can rename the output CSV file as desired.

4.	Run the Model:
•	 Execute the cells in the notebook after the following comment to run the pretrained model.
•	The output will be saved in the data directory.

Part II: Retraining the Model
1.	Prerequisites:
•	Ensure Anaconda is installed on your local machine.
•	Have the training set of images ready for annotation.
•	Clone the necessary repository for annotation: https://github.com/HumanSignal/labelImg

2.	Annotate Images:
•	 Open Anaconda Prompt and navigate to the directory where labelImg is downloaded.
•	Run python labelImg.py to open the labelImg UI.
•	In labelImg, use ‘Open Dir’ to select your training set of images.
•	Use ‘Change Save Dir’ to save the XML annotated set in a desired folder.
•	Create bounding boxes and label them (e.g., cat, human, bird).
•	A training set of around 60 images is recommended (however the more images loaded in the training, the better it is.)

3.	Convert Annotations:
•	Convert XML annotations to TXT format using provided JupyterLab code: https://github.com/dakota-rennels/Python-Notebooks/blob/main/OCR%20and%20Image%20Recognition%20Scripts/xml2txt.py
•	Ensure TXT files are saved in the same folder as their respective images.
•	Copy TXT files into the folder with the training images.

4.	Prepare Training Data:
•	Create a new folder for the training images and upload them with their TXT annotation files.
•	Run the process.py file in the notebook to split images into train and test sets.
 
5.	Train the Model:
•	Execute the cell in the notebook to start training the model.
•	Training may take several hours (minimum 8 hours); the process can run in the background.

6.	Test Model Performance:
•	After training, test the model for Mean Average Precision (mAP) to evaluate performance.

Part III: Configuration Adjustments
If the number of labels (classes) changes, update the yolov4_custom.cfg file.
•	Adjust batches, subdivisions, and filters in the convolutional layer.
•	Use the formula filters = (classes + 5) x3 for filter calculation.
