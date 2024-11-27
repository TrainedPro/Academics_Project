import sqlite3

def connect_database(db_path):
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(db_path)

def fetch_courses_by_program_and_semester(program, semester, cursor):
    """Get courses based on program and semester."""
    query = '''
    SELECT c.course_title
    FROM program_courses pc
    JOIN courses c ON pc.course_code = c.course_code
    WHERE pc.program_name = ? AND pc.semester = ?;
    '''
    cursor.execute(query, (program, semester))
    courses = cursor.fetchall()
    return [course[0] for course in courses]


def get_prerequisite(course_name, cursor):
    """Get prerequisite course code for a given course name."""
    query = '''
    SELECT prerequisite_course_code
    FROM courses
    WHERE course_title = ?;
    '''
    cursor.execute(query, (course_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_eligible_students(db_path, course_name):
    """Get eligible students for a given course."""
    conn = connect_database(db_path)
    cursor = conn.cursor()

    # Get the prerequisite course code for the given course
    prerequisite_course_code = get_prerequisite(course_name, cursor)

    # If the course has a prerequisite, use the appropriate query
    if prerequisite_course_code:
        query = '''
        SELECT 
            s.name
        FROM 
            students s
        JOIN 
            grades g ON s.roll_no = g.roll_no
        JOIN 
            courses c ON g.course_code = c.course_code
        WHERE 
            c.course_title = ? 
            AND NOT (s.warning_status = 2 AND g.grade = '-') -- Exclude students with warning = 2 and grade = '-'
            AND c.prerequisite_course_code = ?  -- Directly check the prerequisite
            AND s.enrollment_status = 'Current';  -- Ensure current enrollment
        '''
        cursor.execute(query, (course_name, prerequisite_course_code))
        students = cursor.fetchall()
    
    # If the course does not have a prerequisite, just check if students are enrolled
    else:
        query = '''
        SELECT 
            s.name
        FROM 
            students s
        JOIN 
            grades g ON s.roll_no = g.roll_no
        JOIN 
            courses c ON g.course_code = c.course_code
        WHERE 
            c.course_title = ? 
            AND NOT (s.warning_status = 2 AND g.grade = '-') -- Exclude students with warning = 2 and grade = '-'
            AND s.enrollment_status = 'Current';  -- Ensure current enrollment
        '''
        cursor.execute(query, (course_name,))
        students = cursor.fetchall()

    conn.close()
    
    return [student[0] for student in students], len(students)


def insert_course(course_code, course_title, credit_hours, prerequisite_course_code):
    """Insert a new course into the database."""
    conn = connect_database('project.sqlite3')
    cursor = conn.cursor()
    
    INSERT_COURSE = '''
    INSERT OR IGNORE INTO courses (
        course_code, course_title, credit_hours, prerequisite_course_code
    ) VALUES (?, ?, ?, ?)
    '''
    cursor.execute(INSERT_COURSE, (course_code, course_title, credit_hours, prerequisite_course_code))
    conn.commit()
    conn.close()
    
def insert_grade(roll_no, course_code, grade):
    """
    Insert a new grade for a student into the grades table.
    If the combination of roll_no and course_code already exists, ignore the insertion.
    """
    conn = connect_database('project.sqlite3')
    cursor = conn.cursor()
    
    INSERT_GRADE = '''
    INSERT OR IGNORE INTO grades (roll_no, course_code, grade)
    VALUES (?, ?, ?)
    '''
    
    try:
        cursor.execute(INSERT_GRADE, (roll_no, course_code, grade))
        conn.commit()
        
        # Check if the row was added
        if cursor.rowcount > 0:
            return f"Grade '{grade}' added for Roll No: {roll_no} in Course: {course_code}."
        else:
            return f"Grade for Roll No: {roll_no} and Course: {course_code} already exists."
    except sqlite3.Error as e:
        return f"Database Error: {str(e)}"
    finally:
        conn.close()
def insert_student(roll_no, name, section, credit_hours_attempted, credit_hours_earned, cgpa, warning_status, enrollment_status, specialization):
    conn = connect_database("project.sqlite3")
    cursor = conn.cursor()
    query = '''
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
    cursor.execute(query, (roll_no, name, section, credit_hours_attempted, credit_hours_earned, cgpa, warning_status, enrollment_status, specialization))
    conn.commit()
    cursor.close()