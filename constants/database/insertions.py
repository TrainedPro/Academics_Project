# SQL queries for database insertions

INSERT_PROGRAM = '''
INSERT OR IGNORE INTO programs (program_name) VALUES (?)
'''

INSERT_COURSE = '''
INSERT OR IGNORE INTO courses (
    course_code, course_title, credit_hours, prerequisite_course_code
) VALUES (?, ?, ?, ?)
'''

INSERT_PROGRAM_COURSE = '''
INSERT OR IGNORE INTO program_courses (program_name, course_code, semester)
VALUES (?, ?, ?)
'''

INSERT_STUDENT = '''
INSERT OR REPLACE INTO students (
    roll_no, 
    name, 
    section,
    credit_hours_attempted, 
    credit_hours_earned, 
    cgpa, 
    warning_status, 
    enrollment_status,
    specialization
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

INSERT_GRADE = '''
INSERT OR IGNORE INTO grades (roll_no, course_code, grade)
VALUES (?, ?, ?)
'''

INSERT_STUDENT = '''
INSERT OR IGNORE INTO Students (
    Roll_No, Name, Cr_Attended, Cr_Earned, Cgpa, Warning, Status
) VALUES (?, ?, ?, ?, ?, ?, ?)
'''

