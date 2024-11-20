import fitz  # PyMuPDF
import sqlite3
from dataclasses import dataclass
from typing import List, Optional, Tuple
import logging
import json


@dataclass
class Course:
    course_code: str
    course_title: str
    credit_hours_class: int
    credit_hours_lab: int
    prerequisites: Optional[str] = None

class CourseProcessor:
    def __init__(self, pdf_path: str, db_path: str = "courses.db"):
        self.pdf_path = pdf_path
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._initialize_database()

    def _initialize_database(self):
        """
        Sets up the database schema if it does not already exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create Programs table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Programs (
                Program_Name TEXT PRIMARY KEY
            )''')

            # Create Courses table (no longer references Program directly)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Courses (
                Course_Code TEXT PRIMARY KEY,
                Course_Title TEXT,
                Credit_Hours_Class INTEGER,
                Credit_Hours_Lab INTEGER,
                Pre_requisites TEXT
            )''')

            # Create Program_Courses table to link Programs and Courses with Semester
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Program_Courses (
                Program_Name TEXT,
                Course_Code TEXT,
                Semester INTEGER,
                PRIMARY KEY (Program_Name, Course_Code, Semester),
                FOREIGN KEY (Program_Name) REFERENCES Programs (Program_Name),
                FOREIGN KEY (Course_Code) REFERENCES Courses (Course_Code)
            )''')

            # Create Prerequisites table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Prerequisites (
                Course_Code TEXT,
                Prerequisite_Code TEXT,
                FOREIGN KEY (Course_Code) REFERENCES Courses (Course_Code),
                FOREIGN KEY (Prerequisite_Code) REFERENCES Courses (Course_Code),
                PRIMARY KEY (Course_Code, Prerequisite_Code)
            )''')

            self.logger.info("Database schema initialized.")


    def extract_course_text(self, program_name: str) -> str:
        """
        Extracts text containing the study plan from the PDF.
        """
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
        """
        Parses the course details from the extracted text.
        """
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
        """
        Inserts courses into the database.
        """
        programs = {program for _, program, _ in courses}
        prerequisites = []

        # Prepare course data and prerequisites
        course_data = []
        program_courses = []  # To store (program_name, course_code, semester) data
        for course, program_name, semester in courses:
            if course.prerequisites:
                # Split prerequisites by ';' and add to prerequisites list
                for prereq in course.prerequisites.split(';'):
                    prerequisites.append((course.course_code, prereq.strip()))

            # Course data: We no longer include program_name in the Courses table
            course_data.append((
                course.course_code, course.course_title, course.credit_hours_class,
                course.credit_hours_lab, course.prerequisites
            ))

            # Program-Courses associations: we store program_name, course_code, and semester in Program_Courses
            program_courses.append((program_name, course.course_code, semester))

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()

            try:
                # Insert programs one by one into Programs table
                self.logger.debug(f"Inserting programs: {programs}")
                for program in programs:
                    try:
                        cursor.execute('INSERT OR IGNORE INTO Programs (Program_Name) VALUES (?)', (program,))
                        self.logger.debug(f"Inserted program: {program}")
                    except sqlite3.Error as e:
                        self.logger.error(f"Error inserting program '{program}': {e}")
                        raise  # Re-raise the error to stop further execution

                # Insert courses one by one into Courses table
                self.logger.debug(f"Inserting courses: {course_data}")
                for course in course_data:
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO Courses (
                                Course_Code, Course_Title, Credit_Hours_Class, Credit_Hours_Lab, Pre_requisites
                            ) VALUES (?, ?, ?, ?, ?)
                        ''', course)
                        self.logger.debug(f"Inserted course: {course}")
                    except sqlite3.Error as e:
                        self.logger.error(f"Error inserting course '{course}': {e}")
                        raise  # Re-raise the error to stop further execution

                # Insert program-course associations into Program_Courses table
                self.logger.debug(f"Inserting program-course associations: {program_courses}")
                for program_course in program_courses:
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO Program_Courses (Program_Name, Course_Code, Semester)
                            VALUES (?, ?, ?)
                        ''', program_course)
                        self.logger.debug(f"Inserted program-course association: {program_course}")
                    except sqlite3.Error as e:
                        self.logger.error(f"Error inserting program-course association '{program_course}': {e}")
                        raise  # Re-raise the error to stop further execution

                # Insert prerequisites one by one into the Prerequisites table
                self.logger.debug(f"Inserting prerequisites: {prerequisites}")
                for prerequisite in prerequisites:
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO Prerequisites (Course_Code, Prerequisite_Code)
                            VALUES (?, ?)
                        ''', prerequisite)
                        self.logger.debug(f"Inserted prerequisite: {prerequisite}")
                    except sqlite3.Error as e:
                        self.logger.error(f"Error inserting prerequisite '{prerequisite}': {e}")
                        raise  # Re-raise the error to stop further execution

                self.logger.info(f"Rows inserted into the database.")
            
            except sqlite3.Error as e:
                # Catch any SQLite error that occurs during the insertions
                self.logger.error(f"Database error occurred: {e}")
                raise  # Re-raise the error to propagate it further
            except Exception as e:
                # Catch any other unexpected error
                self.logger.error(f"Unexpected error occurred: {e}")
                raise  # Re-raise the error to propagate it further

    def process_program(self, program_name: str):
        """
        Orchestrates parsing and database insertion for a single program.
        """
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

    programs = ["Artificial Intelligence", "Computer Science", "Cyber Security", "Data Science", "Software Engineering"]
    for program in programs:
        processor.process_program(program)
