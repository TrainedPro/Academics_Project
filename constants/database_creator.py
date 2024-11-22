import sqlite3

# Connect to the SQLite database (or create one if it doesn't exist)
conn = sqlite3.connect('university.db')
cursor = conn.cursor()

# Create the tables with proper naming conventions
cursor.execute('''
CREATE TABLE IF NOT EXISTS "courses" (
    "course_code" TEXT PRIMARY KEY,
    "course_title" TEXT,
    "credit_hours_class" INTEGER,
    "credit_hours_lab" INTEGER,
    "prerequisites" TEXT
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS "grades" (
    "roll_no" TEXT,
    "grade" TEXT,
    "course_code" TEXT,
    PRIMARY KEY("roll_no", "course_code"),
    FOREIGN KEY("course_code") REFERENCES "courses"("course_code"),
    FOREIGN KEY("roll_no") REFERENCES "students"("roll_no")
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS "course_prerequisites" (
    "course_code" TEXT,
    "prerequisite_code" TEXT,
    PRIMARY KEY("course_code", "prerequisite_code"),
    FOREIGN KEY("course_code") REFERENCES "courses"("course_code"),
    FOREIGN KEY("prerequisite_code") REFERENCES "courses"("course_code")
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS "program_courses" (
    "program_name" TEXT,
    "course_code" TEXT,
    "semester" INTEGER,
    PRIMARY KEY("program_name", "course_code", "semester"),
    FOREIGN KEY("course_code") REFERENCES "courses"("course_code"),
    FOREIGN KEY("program_name") REFERENCES "programs"("program_name")
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS "programs" (
    "program_name" TEXT PRIMARY KEY
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS "students" (
    "name" TEXT,
    "roll_no" TEXT PRIMARY KEY,
    "cr_attended" INTEGER,
    "cr_earned" INTEGER,
    "cgpa" REAL,
    "warning" INTEGER,
    "status" TEXT
);
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
