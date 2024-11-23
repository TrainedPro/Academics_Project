import pandas as pd
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('university.db')
cursor = conn.cursor()

# Function to get course code from the course name
def get_course_code(course_name):
    # Extract the part before the first hyphen ('-') to get the course title
    course_title = course_name.split('-')[0].strip()
    
    # Query the course code from the database
    cursor.execute("SELECT course_code FROM courses WHERE course_title = ?", (course_title,))
    result = cursor.fetchone()
    
    # Return the course code if found, otherwise return None
    return result[0] if result else None

# Function to insert grades into the 'grades' table
def insert_grades_from_excel(file_path):
    # Read the Excel file (skip first row if it's empty or metadata)
    excel_data = pd.read_excel(file_path, header=1, usecols="A:Z")  # Assuming columns A to Z are relevant, adjust if needed

    # Loop through the rows of the Excel data (for each student)
    for _, row in excel_data.iterrows():
        roll_no = row['Roll No']  # Assuming 'Roll No' is the first column
        
        # Start processing from the 11th column (index 10 in zero-based indexing)
        for column_index, (column_name, grade) in enumerate(row.items()):
            if column_index >= 10 and pd.notna(grade):  # Skip columns before the 11th and empty grades
                course_name = column_name
                course_code = get_course_code(course_name)
                
                if course_code:
                    # Insert the grade into the grades table
                    cursor.execute('''
                        INSERT OR REPLACE INTO grades (roll_no, course_code, grade)
                        VALUES (?, ?, ?)
                    ''', (roll_no, course_code, grade))

    # Commit the changes and close the connection
    conn.commit()

# Example usage
insert_grades_from_excel('grade_report_22.xlsx')  # Provide the correct path to your Excel file

# Close the connection to the database
conn.close()
