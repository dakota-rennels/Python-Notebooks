import os

# Define a dictionary to map class names to their corresponding IDs
class_names = {
    "example_class": 0,
}

# Function to convert an XML file to YOLO format
def convert_xml_to_yolo(xml_file, class_names):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Get the size of the image
    size = root.find('size')
    img_width = int(size.find('width').text)
    img_height = int(size.find('height').text)

    yolo_data = []
    for obj in root.findall('object'):
        class_name = obj.find('name').text
        if class_name in class_names:
            class_id = class_names[class_name]

            bndbox = obj.find('bndbox')
            xmin = int(bndbox.find('xmin').text)
            ymin = int(bndbox.find('ymin').text)
            xmax = int(bndbox.find('xmax').text)
            ymax = int(bndbox.find('ymax').text)

            x_center = ((xmin + xmax) / 2) / img_width
            y_center = ((ymin + ymax) / 2) / img_height
            width = (xmax - xmin) / img_width
            height = (ymax - ymin) / img_height

            yolo_data.append(f"{class_id} {x_center} {y_center} {width} {height}")

    return yolo_data

# Directory containing the XML files
xml_directory = 'model_data'

# Convert each XML file to a YOLO format text file
for xml_file in os.listdir(xml_directory):
    if xml_file.endswith('.xml'):
        xml_path = os.path.join(xml_directory, xml_file)
        yolo_data = convert_xml_to_yolo(xml_path, class_names)
        
        # Save the YOLO format data to a text file
        txt_path = xml_path.replace('.xml', '.txt')
        with open(txt_path, 'w') as file:
            file.write('\n'.join(yolo_data))

print("Conversion complete.")
