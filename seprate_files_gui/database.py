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

    prerequisite_course_code = get_prerequisite(course_name, cursor)
    
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
            AND g.grade IN ('-', 'F', 'W', 'I')
            AND EXISTS (
                SELECT 1
                FROM courses prerequisite
                WHERE prerequisite.course_code = c.prerequisite_course_code
                AND prerequisite.course_code = ?
            );
        '''
        cursor.execute(query, (course_name, prerequisite_course_code))
        students = cursor.fetchall()
        conn.close()

        return [student[0] for student in students], len(students)

    conn.close()
    return [], 0

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