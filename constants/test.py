import pandas as pd

# Read the Excel file (make sure the file path is correct)
excel_file = 'grade_report_22.xlsx'

# Read the Excel file
df = pd.read_excel(excel_file, header=1)

# Print the column names to check for issues
print("Column Names in the Excel File:")
print(df.columns)

# Optional: Strip whitespace from column names to avoid issues with hidden spaces
df.columns = df.columns.str.strip()

# Now try accessing the column again
print(df['Roll No'])
