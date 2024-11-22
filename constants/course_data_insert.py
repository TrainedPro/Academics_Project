import pandas as pd
import sqlite3

# Read data from the CSV file
csv_file = "course_data.csv"  # Replace with the path to your CSV file
df = pd.read_csv(csv_file)

# Ensure 'Credits (Theory + Lab)' is properly formatted and split into class and lab hours
df['credit_hours_class'] = 0
df['credit_hours_lab'] = 0

for index, row in df.iterrows():
    credits = row['Credits (Theory + Lab)']
    if pd.isna(credits) or '+' not in str(credits):
        theory, lab = 0, 0
    else:
        theory, lab = map(int, credits.split('+'))
    df.at[index, 'credit_hours_class'] = theory
    df.at[index, 'credit_hours_lab'] = lab

# Connect to SQLite database
conn = sqlite3.connect("university.db")
cursor = conn.cursor()

# Create the `courses` table if it doesn't already exist

# Insert data into the table
for index, row in df.iterrows():
    cursor.execute('''
    INSERT INTO courses (course_code, course_title, credit_hours_class, credit_hours_lab, prerequisites)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        row['Course Code'],  # Adjust column names as per your CSV
        row['Course Title'],
        row['credit_hours_class'],
        row['credit_hours_lab'],
        row.get('Prerequisite', None),  # Handle missing prerequisites gracefully
    ))

# Commit changes and close the connection
conn.commit()
conn.close()
