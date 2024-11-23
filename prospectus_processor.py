import fitz  # PyMuPDF
import sqlite3
from dataclasses import dataclass
from typing import List, Optional, Tuple
import logging
import json

from constants.database import config
from constants.database import schema
from constants.database import insertions

@dataclass
class Course:
    course_code: str
    course_title: str
    credit_hours_class: int
    credit_hours_lab: int
    prerequisites: Optional[str] = None

class CourseProcessor:
    programs = ["Artificial Intelligence", "Computer Science", "Cyber Security", "Data Science", "Software Engineering"]
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.db_path = config.DB_NAME
        self.logger = logging.getLogger(__name__)
        self._initialize_database()

    def _initialize_database(self):
        """Sets up the database schema if it does not already exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables using schema constants
            cursor.execute(schema.CREATE_PROGRAMS_TABLE)
            cursor.execute(schema.CREATE_COURSES_TABLE)
            cursor.execute(schema.CREATE_PROGRAM_COURSES_TABLE)
            cursor.execute(schema.CREATE_PREREQUISITES_TABLE)

            self.logger.info("Database schema initialized.")

    def extract_course_text(self, program_name: str) -> str:
        """Extracts text containing the study plan from the PDF."""
        search_term = f"Tentative Study Plan-Bachelor of Science ({program_name})"
        try:
            with fitz.open(self.pdf_path) as doc:
                for page_number in range(len(doc)):
                    page = doc[page_number]
                    text = page.get_text()
                    if search_term in text:
                        self.logger.info(f"Found study plan for {program_name} on page {page_number + 1}")
                        return text
                raise ValueError(f"Search term '{search_term}' not found.")
        except FileNotFoundError:
            self.logger.error(f"File '{self.pdf_path}' not found.")
            raise
        except Exception as e:
            self.logger.error(f"Error processing PDF: {e}")
            raise

    def parse_courses(self, text: str, program_name: str) -> List[Course]:
        """Parses the course details from the extracted text."""
        lines = [line.strip() for line in text.split('\n')]
        courses = []
        idx, semester, total_count = 0, 0, 0

        while 'Semester-I' not in lines[idx]:
            idx += 1

        while idx < len(lines):
            if 'Total' in lines[idx]:
                idx += 3
                total_count += 1
                if total_count >= 8:
                    break
            elif 'Semester-' in lines[idx]:
                semester += 1
                idx += 1
            else:
                course_code, idx = self._extract_multiline_code(lines, idx)
                course_title, idx = self._extract_multiline_title(lines, idx)
                credit_hours_class, idx = int(lines[idx]), idx + 1
                credit_hours_lab, idx = int(lines[idx]), idx + 1
                prereq = lines[idx] if lines[idx] != '—' else None
                idx += 1
                course = Course(
                    course_code=course_code,
                    course_title=course_title,
                    credit_hours_class=credit_hours_class,
                    credit_hours_lab=credit_hours_lab,
                    prerequisites=prereq,
                )
                self.logger.debug(f"Parsed course: {json.dumps(course.__dict__, indent=2)}")
                courses.append((course, program_name, semester))  # Include program_name and semester
        return courses

    def _extract_multiline_code(self, lines: List[str], idx: int) -> Tuple[str, int]:
        course_code = lines[idx]
        idx += 1
        while course_code[-1] == '/':
            course_code += lines[idx]
            idx += 1
        return course_code, idx

    def _extract_multiline_title(self, lines: List[str], idx: int) -> Tuple[str, int]:
        course_title = lines[idx]
        idx += 1
        while not lines[idx].isdigit():
            course_title += ' ' + lines[idx]
            idx += 1
        return course_title, idx

    def insert_courses(self, courses: List[Tuple[Course, str, int]]):
        """Inserts courses into the database."""
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

            try:
                # Bulk insertions
                self.logger.debug(f"Inserting programs: {programs}")
                cursor.executemany('INSERT OR IGNORE INTO Programs (Program_Name) VALUES (?)', [(program,) for program in programs])

                self.logger.debug(f"Inserting courses: {course_data}")
                cursor.executemany('''
                    INSERT OR IGNORE INTO Courses (
                        Course_Code, Course_Title, Credit_Hours_Class, Credit_Hours_Lab, Pre_requisites
                    ) VALUES (?, ?, ?, ?, ?)
                ''', course_data)

                self.logger.debug(f"Inserting program-course associations: {program_courses}")
                cursor.executemany('''
                    INSERT OR IGNORE INTO Program_Courses (Program_Name, Course_Code, Semester)
                    VALUES (?, ?, ?)
                ''', program_courses)

                self.logger.debug(f"Inserting prerequisites: {prerequisites}")
                cursor.executemany('''
                    INSERT OR IGNORE INTO Prerequisites (Course_Code, Prerequisite_Code)
                    VALUES (?, ?)
                ''', prerequisites)

                conn.commit()
                self.logger.info(f"Rows inserted into the database.")
            except sqlite3.Error as e:
                self.logger.error(f"Error inserting data into database: {e}")
                conn.rollback()
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error occurred: {e}")
                raise

    def process_program(self, program_name: str):
        """Orchestrates parsing and database insertion for a single program."""
        try:
            text = self.extract_course_text(program_name)
            courses = self.parse_courses(text, program_name)
            self.insert_courses(courses)
        except Exception as e:
            self.logger.error(f"Failed to process program '{program_name}': {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s (line %(lineno)d)",
        handlers=[
            logging.FileHandler("course_processor.log"),
            logging.StreamHandler()
        ]
    )

    pdf_path = "Computing Programs.pdf"
    processor = CourseProcessor(pdf_path)

    for program in CourseProcessor.programs:
        processor.process_program(program)
