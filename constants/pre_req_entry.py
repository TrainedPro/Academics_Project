import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("university.db")
cursor = conn.cursor()


# Retrieve courses and their prerequisites from the courses table
cursor.execute('SELECT course_code, prerequisites FROM courses')
courses = cursor.fetchall()

# Populate the course_prerequisites table
for course_code, prerequisites in courses:
    if prerequisites:  # Ensure prerequisites field is not null or empty
        prerequisite_codes = prerequisites.split(',')  # Split if multiple prerequisites
        for prerequisite_code in prerequisite_codes:
            prerequisite_code = prerequisite_code.strip()  # Clean whitespace
            cursor.execute('''
            INSERT OR IGNORE INTO course_prerequisites (course_code, prerequisite_code)
            VALUES (?, ?)
            ''', (course_code, prerequisite_code))

# Commit changes and close the connection
conn.commit()
conn.close()
