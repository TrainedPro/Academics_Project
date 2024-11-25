# Database Schema Constants for table creation

CREATE_TABLE_PROGRAMS = '''
CREATE TABLE IF NOT EXISTS programs (
    program_name TEXT PRIMARY KEY
)
'''

CREATE_TABLE_COURSES = '''
CREATE TABLE IF NOT EXISTS courses (
    course_code TEXT PRIMARY KEY,
    course_title TEXT NOT NULL,
    credit_hours INTEGER NOT NULL,
    prerequisite_course_code TEXT,
    FOREIGN KEY (prerequisite_course_code) REFERENCES courses (course_code)
)
'''

CREATE_TABLE_PROGRAM_COURSES = '''
CREATE TABLE IF NOT EXISTS program_courses (
    program_name TEXT NOT NULL,
    course_code TEXT NOT NULL,
    semester INTEGER NOT NULL,
    PRIMARY KEY (program_name, course_code, semester),
    FOREIGN KEY (program_name) REFERENCES programs (program_name),
    FOREIGN KEY (course_code) REFERENCES courses (course_code)
)
'''

#? Range of student warnings
CREATE_TABLE_STUDENTS = '''
CREATE TABLE IF NOT EXISTS students (
    roll_no TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    section TEXT NOT NULL,
    credit_hours_attempted INTEGER NOT NULL,
    credit_hours_earned INTEGER NOT NULL,
    cgpa REAL NOT NULL,
    warning_status INTEGER NOT NULL CHECK (warning_status BETWEEN 0 AND 3),
    enrollment_status TEXT NOT NULL,
    specialization TEXT
)
'''

CREATE_TABLE_GRADES = '''
CREATE TABLE IF NOT EXISTS grades (
    roll_no TEXT NOT NULL,
    course_code TEXT NOT NULL,
    grade TEXT NOT NULL,
    PRIMARY KEY (roll_no, course_code),
    FOREIGN KEY (roll_no) REFERENCES students (roll_no)
    FOREIGN KEY (course_code) REFERENCES courses (course_code)
)
'''
