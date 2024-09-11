import sqlite3
import csv

# Connect to SQLite database
conn = sqlite3.connect('courses.db')
cursor = conn.cursor()



# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS Programs (
    Program_Name TEXT PRIMARY KEY
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Courses (
    Course_Code TEXT PRIMARY KEY,
    Program_Name TEXT,
    Semester INTEGER,
    Course_Title TEXT,
    Credit_Hours_Class INTEGER,
    Credit_Hours_Lab INTEGER,
    Pre_requisites TEXT,  -- Stores prerequisites as a semicolon-separated string
    FOREIGN KEY (Program_Name) REFERENCES Programs (Program_Name)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Prerequisites (
    Course_Code TEXT,
    Prerequisite_Code TEXT,
    FOREIGN KEY (Course_Code) REFERENCES Courses (Course_Code),
    FOREIGN KEY (Prerequisite_Code) REFERENCES Courses (Course_Code),
    PRIMARY KEY (Course_Code, Prerequisite_Code)
)
''')

# Read data from CSV and insert into database
csv_file_path = '_Data_Science_Courses.csv'  # Update this path to your CSV file

with open(csv_file_path, 'r') as file:
    reader = csv.DictReader(file)
    
    programs = set()
    courses = []
    
    for row in reader:
        program_name = row['Program Name']
        programs.add((program_name,))
        
        course_code = row['Course Code']
        semester = int(row['Semester'])
        course_title = row['Course Title']
        credit_hours_class = int(row['Credit Hours (Class)'])
        credit_hours_lab = int(row['Credit Hours (Lab)'])
        prerequisites = row['Pre-requisites'] or None
        
        courses.append((
            course_code, program_name, semester, course_title, 
            credit_hours_class, credit_hours_lab, prerequisites
        ))

# Insert Programs into database
cursor.executemany('''
INSERT OR IGNORE INTO Programs (Program_Name) VALUES (?)
''', programs)

# Insert Courses into database
cursor.executemany('''
INSERT OR IGNORE INTO Courses (
    Course_Code, Program_Name, Semester, Course_Title, Credit_Hours_Class, Credit_Hours_Lab, Pre_requisites
) VALUES (?, ?, ?, ?, ?, ?, ?)
''', courses)

# Extract and insert prerequisites into the Prerequisites table
cursor.execute('SELECT Course_Code, Pre_requisites FROM Courses')
courses = cursor.fetchall()

prerequisites = []
for course_code, pre_reqs in courses:
    if pre_reqs:
        pre_reqs_list = pre_reqs.split(';')
        for pre_req in pre_reqs_list:
            if pre_req:
                prerequisites.append((course_code, pre_req))

cursor.executemany('''
INSERT OR IGNORE INTO Prerequisites (Course_Code, Prerequisite_Code) VALUES (?, ?)
''', prerequisites)

# Print the Prerequisites table content
cursor.execute('SELECT * FROM Prerequisites')
rows = cursor.fetchall()
for row in rows:
    print(row)
    
cursor.execute("")

# Commit changes and close the connection
conn.commit()
conn.close()

print("CSV data inserted and prerequisites table updated successfully.")
