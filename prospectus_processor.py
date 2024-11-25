from dataclasses import dataclass
from typing import List, Tuple, Optional  # Add these imports
import sqlite3
import logging
import json

# Define the Course class first
@dataclass
class Course:
    course_code: str
    course_title: str
    credit_hours_class: int
    credit_hours_lab: int
    prerequisites: Optional[str] = None

# Now define the CourseProcessor class
class CourseProcessor:
    def __init__(self, pdf_path: str, db_path: str = "courses.db"):
        self.pdf_path = pdf_path
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._initialize_database()

    def insert_courses(self, courses: List[Tuple[Course, str, int]]):
        """
        Inserts courses into the database.
        """
        programs = {program for _, program, _ in courses}
        prerequisites = []
        course_data = []
        program_courses = []

        for course, program_name, semester in courses:
            if course.prerequisites:
                for prereq in course.prerequisites.split(';'):
                    prerequisites.append((course.course_code, prereq.strip()))

            course_data.append((
                course.course_code, course.course_title, course.credit_hours_class,
                course.credit_hours_lab, course.prerequisites
            ))
            program_courses.append((program_name, course.course_code, semester))

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()

            for program in programs:
                cursor.execute('INSERT OR IGNORE INTO Programs (Program_Name) VALUES (?)', (program,))
            for course in course_data:
                cursor.execute('''
                    INSERT OR IGNORE INTO Courses (
                        Course_Code, Course_Title, Credit_Hours_Class, Credit_Hours_Lab, Pre_requisites
                    ) VALUES (?, ?, ?, ?, ?)
                ''', course)
            for program_course in program_courses:
                cursor.execute('''
                    INSERT OR IGNORE INTO Program_Courses (Program_Name, Course_Code, Semester)
                    VALUES (?, ?, ?)
                ''', program_course)
            for prerequisite in prerequisites:
                cursor.execute('''
                    INSERT OR IGNORE INTO Prerequisites (Course_Code, Prerequisite_Code)
                    VALUES (?, ?)
                ''', prerequisite)

            self.logger.info("Data inserted into the database.")
