import fitz  # PyMuPDF
import sqlite3
from dataclasses import dataclass
from typing import List, Optional, Tuple
import logging

from constants.database import config
from constants.database import schema
from constants.database import insertions

@dataclass
class Course:
    course_code: str
    course_title: str
    credit_hours: int
    prerequisite_course_code: Optional[str] = None

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
            cursor.execute(schema.CREATE_TABLE_PROGRAMS)
            cursor.execute(schema.CREATE_TABLE_COURSES)
            cursor.execute(schema.CREATE_TABLE_PROGRAM_COURSES)

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
    
    def append_courses_and_labs(courses: List[Tuple[Course, str, int]],
                                course_code: str, course_title: str,
                                credit_hours_class: int, credit_hours_lab: int,
                                prereq: str, program_name: str, semester: int) -> None:
        """
        Appends the base course and lab course (if applicable) to the courses list.

        Args:
            courses: The list of courses to append to.
            course_code: The course code.
            course_title: The course title.
            credit_hours_class: The credit hours for the class.
            credit_hours_lab: The credit hours for the lab.
            prereq: Prerequisite course code (if any).
            program_name: The program name.
            semester: The semester number.
        """
        # Append the base course
        courses.append((Course(
            course_code=course_code,
            course_title=course_title,
            credit_hours=credit_hours_class + (credit_hours_lab if credit_hours_lab > 1 else 0),
            prerequisite_course_code=prereq,
        ), program_name, semester))

        # Append the lab course if lab credits = 1
        if credit_hours_lab == 1:
            lab_code = course_code[:1] + 'L' + course_code[2:]
            lab_title = f"{course_title} - Lab"
            courses.append((Course(
                course_code=lab_code,
                course_title=lab_title,
                credit_hours=1,
                prerequisite_course_code=prereq,
            ), program_name, semester))

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

                # Use the helper function to append courses and labs
                self.append_courses_and_labs(
                    courses, course_code, course_title,
                    credit_hours_class, credit_hours_lab,
                    prereq, program_name, semester
                )

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
        course_data = []
        program_courses = []

        for course, program_name, semester in courses:
            course_data.append((
                course.course_code, course.course_title, course.credit_hours, course.prerequisite_course_code
            ))
            program_courses.append((program_name, course.course_code, semester))

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()

            try:
                # Bulk insertions
                self.logger.debug(f"Inserting programs: {programs}")
                cursor.executemany(insertions.INSERT_PROGRAM, [(program,) for program in programs])

                # Insert all courses first (ignoring prerequisites for now)
                course_data = [
                    (course.course_code, course.course_title, course.credit_hours, None)
                    for course, _, _ in courses
                ]
                cursor.executemany(insertions.INSERT_COURSE, course_data)

                # Update prerequisites after all courses are inserted
                # ensures foreign key constraints are met
                update_query = '''
                UPDATE courses
                SET prerequisite_course_code = ?
                WHERE course_code = ?
                '''
                prerequisites_data = [
                    (course.prerequisite_course_code, course.course_code)
                    for course, _, _ in courses if course.prerequisite_course_code
                ]
                cursor.executemany(update_query, prerequisites_data)


                self.logger.debug(f"Inserting program-course associations: {program_courses}")
                cursor.executemany(insertions.INSERT_PROGRAM_COURSE, program_courses)
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
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("course_processor.log"),
            logging.StreamHandler()
        ]
    )

    #! change for the GUI
    pdf_path = "Computing Programs.pdf"
    processor = CourseProcessor(pdf_path)

    for program in CourseProcessor.programs:
        processor.process_program(program)
