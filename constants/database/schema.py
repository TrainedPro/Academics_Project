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
    credit_hours_class INTEGER NOT NULL,
    credit_hours_lab INTEGER NOT NULL,
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
    credit_hours_attempted INTEGER NOT NULL,
    credit_hours_earned INTEGER NOT NULL,
    cgpa REAL NOT NULL,
    warning_status INTEGER NOT NULL CHECK (warning_status BETWEEN 0 AND 3),
    enrollment_status TEXT NOT NULL
)
'''