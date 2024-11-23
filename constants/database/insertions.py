# SQL queries for database insertions

INSERT_PROGRAM = '''
INSERT OR IGNORE INTO Programs (Program_Name) VALUES (?)
'''

INSERT_COURSE = '''
INSERT OR IGNORE INTO Courses (
    Course_Code, Course_Title, Credit_Hours_Class, Credit_Hours_Lab, Pre_requisites
) VALUES (?, ?, ?, ?, ?)
'''

INSERT_PROGRAM_COURSE = '''
INSERT OR IGNORE INTO Program_Courses (Program_Name, Course_Code, Semester)
VALUES (?, ?, ?)
'''

INSERT_PREREQUISITE = '''
INSERT OR IGNORE INTO Prerequisites (Course_Code, Prerequisite_Code)
VALUES (?, ?)
'''
