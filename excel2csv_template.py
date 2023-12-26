# Uncomment line below to install the library to the kernel for excel import, if needed
#pip install openpyxl

# Import Library
import pandas as pd

# Specify the paths to the input XLSX files
xlsx_file = 'ENETER EXCEL FILE PATH HERE' #Enter your current excel file path

# Specify the paths to the output CSV files
csv_file = 'ENTER PATH FOR NEW CSV FILE' #Enter your desired csv file destination

# Read the XLSX files into DataFrames
df = pd.read_excel(xlsx_file)

# Write the DataFrame to a CSV file
df.to_csv(csv_file, index=False)
