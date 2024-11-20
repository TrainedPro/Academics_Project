import pandas as pd
import sqlite3

# Load data from CSV files
grades_df = pd.read_csv("grade.csv", skiprows=1)
courses_df = pd.read_csv("data.csv")

# Ensure columns are correct
print(grades_df.columns)
print(courses_df.columns)

# Connect to SQLite database
conn = sqlite3.connect('university.db')
cursor = conn.cursor()

# Drop tables if they exist (optional, for development)
cursor.execute("DROP TABLE IF EXISTS Students")
cursor.execute("DROP TABLE IF EXISTS Courses")
cursor.execute("DROP TABLE IF EXISTS Grades")

# Create tables with proper foreign keys
cursor.execute('''
CREATE TABLE IF NOT EXISTS Students (
    Roll_No TEXT PRIMARY KEY,
    Name TEXT,
    Section TEXT,
    CrAtt INTEGER,
    CrErnd INTEGER,
    CGPA REAL,
    Wrng INTEGER,
    Status TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Courses (
    Course_Code TEXT PRIMARY KEY,
    Course_Title TEXT,
    Credits_Theory INTEGER,
    Credits_Lab INTEGER,
    Prerequisite TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Grades (
    Roll_No TEXT,
    Course_Code TEXT,
    Grade TEXT,
    FOREIGN KEY(Roll_No) REFERENCES Students(Roll_No),
    FOREIGN KEY(Course_Code) REFERENCES Courses(Course_Code)
)
''')

# Insert students data
students_data = grades_df[['Sr.#', 'Roll No', 'Name', 'Sec', 'CrAtt', 'CrErnd', 'CGPA', 'Wrng', 'Status']].drop_duplicates()
students_data.columns = ['Sr_Num', 'Roll_No', 'Name', 'Section', 'CrAtt', 'CrErnd', 'CGPA', 'Wrng', 'Status']
students_data = students_data.drop(columns=['Sr_Num'])  # Remove unnecessary column
students_data.to_sql('Students', conn, if_exists='replace', index=False)

# Insert courses data
courses_data = courses_df[['Course Code', 'Course Title', 'Credits (Theory + Lab)', 'Prerequisite']].copy()
courses_data[['Credits_Theory', 'Credits_Lab']] = courses_data['Credits (Theory + Lab)'].str.split('+', expand=True).astype(int)
courses_data = courses_data.drop(columns=['Credits (Theory + Lab)'])
courses_data.columns = ['Course_Code', 'Course_Title', 'Prerequisite', 'Credits_Theory', 'Credits_Lab']
courses_data.to_sql('Courses', conn, if_exists='replace', index=False)

# Insert grades data
grade_columns = grades_df.columns[10:]  # Start from the 11th column where course grades begin
grades_data = grades_df.melt(id_vars=['Roll No'], value_vars=grade_columns, var_name='Course', value_name='Grade')
grades_data['Course_Code'] = grades_data['Course'].str.extract(r'-([A-Z]+\d+)$')  # Extract course code from column name
grades_data = grades_data.dropna(subset=['Grade', 'Course_Code'])
grades_data = grades_data[['Roll No', 'Course_Code', 'Grade']]
grades_data.columns = ['Roll_No', 'Course_Code', 'Grade']
grades_data.to_sql('Grades', conn, if_exists='replace', index=False)

# Commit changes
conn.commit()

# Verify proper joins with Course_Title
query = '''
SELECT 
    Grades.Roll_No,
    Students.Name,
    Grades.Course_Code,
    Courses.Course_Title,
    Grades.Grade
FROM Grades
JOIN Students ON Grades.Roll_No = Students.Roll_No
JOIN Courses ON Grades.Course_Code = Courses.Course_Code
'''

result = pd.read_sql_query(query, conn)
print(result)

# Close the connection
conn.close()

print("Database created and populated successfully.")
