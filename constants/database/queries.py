fetch_regular_courses = '''
    SELECT 
        courses.course_code, 
        courses.course_title, 
        courses.credit_hours, 
        courses.prerequisite_course_code
    FROM 
        program_courses
    JOIN 
        courses
    ON 
        program_courses.course_code = courses.course_code
    WHERE 
        program_courses.program_name = ? 
        AND program_courses.semester = ?
    ORDER BY 
        courses.course_title;
    '''


#use to get prereq of any course   
get_prerequisite_query = '''
    SELECT prerequisite_course_code
    FROM courses
    WHERE course_title = ?;
    '''

# Query to count eligible students based on passing the prerequisite course
get_eligible_students = '''
        SELECT 
            COUNT(DISTINCT s.roll_no) AS eligible_students
        FROM 
            students s
        JOIN 
            grades g
        ON 
            s.roll_no = g.roll_no
        JOIN 
            courses c
        ON 
            g.course_code = c.course_code
        WHERE 
            c.course_title = ? 
            AND g.grade  IN ('-', 'F', 'W', 'I')
            AND EXISTS (
                SELECT 1
                FROM courses prerequisite
                WHERE prerequisite.course_code = c.prerequisite_course_code
                AND prerequisite.course_code = ?
            );
        '''
