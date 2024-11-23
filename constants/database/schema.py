# Database Schema Constants for table creation

CREATE_PROGRAMS_TABLE = '''
CREATE TABLE IF NOT EXISTS Programs (
    Program_Name TEXT PRIMARY KEY
)
'''

CREATE_COURSES_TABLE = '''
CREATE TABLE IF NOT EXISTS Courses (
    Course_Code TEXT PRIMARY KEY,
    Course_Title TEXT,
    Credit_Hours_Class INTEGER,
    Credit_Hours_Lab INTEGER,
    Pre_requisites TEXT
)
'''

CREATE_PROGRAM_COURSES_TABLE = '''
CREATE TABLE IF NOT EXISTS Program_Courses (
    Program_Name TEXT,
    Course_Code TEXT,
    Semester INTEGER,
    PRIMARY KEY (Program_Name, Course_Code, Semester),
    FOREIGN KEY (Program_Name) REFERENCES Programs (Program_Name),
    FOREIGN KEY (Course_Code) REFERENCES Courses (Course_Code)
)
'''

CREATE_PREREQUISITES_TABLE = '''
CREATE TABLE IF NOT EXISTS Prerequisites (
    Course_Code TEXT,
    Prerequisite_Code TEXT,
    FOREIGN KEY (Course_Code) REFERENCES Courses (Course_Code),
    FOREIGN KEY (Prerequisite_Code) REFERENCES Courses (Course_Code),
    PRIMARY KEY (Course_Code, Prerequisite_Code)
)
'''