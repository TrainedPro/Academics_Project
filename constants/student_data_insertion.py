import pandas as pd
import sqlite3

# Path to your Excel file
excel_file = 'grade_report_22.xlsx'

# Read the Excel file with the header in the first row
df = pd.read_excel(excel_file, header=1)

# Connect to SQLite database (replace with your actual database path)
conn = sqlite3.connect('university.db')
cursor = conn.cursor()

# Insert data into the 'Students' table
for index, row in df.iterrows():
    # Extract values from the row
    roll_no = row['Roll No']
    name = row['Name']
   # sec = row['Sec']
    cr_attended = row['CrAtt']
    cr_earned = row['CrErnd']
    cgpa = row['CGPA']
    warning = row['Wrng']
    status = row['Status']
    
    # Insert into the Students table
    cursor.execute("""
    INSERT INTO Students
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, roll_no, cr_attended, cr_earned, cgpa, warning, status))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data inserted successfully.")
