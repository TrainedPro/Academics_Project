import pandas as pd
import sqlite3

# Load XLSX file
xlsx_file = "grade_report_22.xlsx"  # Replace with your file path
grades_df = pd.read_excel(xlsx_file,header=1)

# Connect to SQLite database
conn = sqlite3.connect("university.db")
cursor = conn.cursor()

# Ensure the grades table exists
# Insert grades data
for index, row in grades_df.iterrows():
    roll_no = row['Roll No']
    course_code = row['Course Code']
    grade = row['Grade']
    
    # Ensure roll_no and course_code exist in their respective tables
    cursor.execute('SELECT COUNT(*) FROM students WHERE roll_no = ?', (roll_no,))
    student_exists = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM courses WHERE course_code = ?', (course_code,))
    course_exists = cursor.fetchone()[0]
    
    if student_exists and course_exists:  # Only insert if both exist
        cursor.execute('''
        INSERT OR IGNORE INTO grades (roll_no, grade, course_code)
        VALUES (?, ?, ?)
        ''', (roll_no, grade, course_code))

# Commit changes and close the connection
conn.commit()
conn.close()
