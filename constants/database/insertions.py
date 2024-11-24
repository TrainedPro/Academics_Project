# SQL queries for database insertions

INSERT_PROGRAM = '''
INSERT OR IGNORE INTO programs (program_name) VALUES (?)
'''

INSERT_COURSE = '''
INSERT OR IGNORE INTO courses (
    course_code, course_title, credit_hours_class, credit_hours_lab, prerequisites
) VALUES (?, ?, ?, ?, ?)
'''

INSERT_PROGRAM_COURSE = '''
INSERT OR IGNORE INTO program_courses (program_name, course_code, semester)
VALUES (?, ?, ?)
'''
