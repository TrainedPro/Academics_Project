import csv
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass

from constants.database.config import DB_NAME
from constants.database.insertions import INSERT_STUDENT

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Student:
    """Data class to represent a student record."""
    roll_no: str
    name: str
    section: str
    credit_hours_attempted: int
    credit_hours_earned: int
    cgpa: float
    warning_status: int
    enrollment_status: str
    specialization: str
    grades: Dict[str, str]  # course_code: grade

class CourseValidator:
    """Handles course validation against the database."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.valid_courses: Set[str] = set()
        self._load_valid_courses()
    
    def _load_valid_courses(self) -> None:
        """Load all valid course codes from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT course_code FROM courses")
                self.valid_courses = {row[0] for row in cursor.fetchall()}
                logger.info(f"Loaded {len(self.valid_courses)} valid courses from database")
        except sqlite3.Error as e:
            logger.error(f"Error loading courses from database: {e}")
            raise

    def parse_course_info(self, course_column: str) -> Tuple[str, str]:
        """Parse course title and code from column header."""
        try:
            # Split on the last occurrence of '-'
            parts = course_column.rsplit('-', 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid course format: {course_column}")
            
            course_title = parts[0].strip()
            course_code = parts[1].strip()
            return course_title, course_code
        except Exception as e:
            logger.error(f"Error parsing course info from '{course_column}': {e}")
            raise

    def validate_course(self, course_column: str) -> Tuple[bool, str]:
        """Validate a course against the database."""
        try:
            _, course_code = self.parse_course_info(course_column)
            is_valid = course_code in self.valid_courses
            if not is_valid:
                return False, f"Course code '{course_code}' not found in database"
            return True, course_code
        except Exception as e:
            return False, str(e)

class GradeParser:
    """Handles parsing of grade CSV file and database operations."""
    
    def __init__(self, db_path: str = DB_NAME):
        """Initialize the parser with database path."""
        self.db_path = db_path
        self.course_validator = CourseValidator(db_path)
        self.invalid_courses: Dict[str, str] = {}  # course_column: error_message
    
    def parse_csv(self, file_path: str) -> List[Student]:
        """Parse the CSV file and return a list of Student objects."""
        try:
            students = []
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                
                # Skip the first row (BS(SE))
                next(csv_reader)
                
                # Get headers and validate courses
                headers = next(csv_reader)
                course_columns = headers[10:]  # Columns after specialization
                
                # Validate all courses before processing
                for course_column in course_columns:
                    is_valid, message = self.course_validator.validate_course(course_column)
                    if not is_valid:
                        self.invalid_courses[course_column] = message
                
                if self.invalid_courses:
                    logger.warning("Found invalid courses:")
                    for course, error in self.invalid_courses.items():
                        logger.warning(f"  - {course}: {error}")
                
                # Process each student row
                for row in csv_reader:
                    if not row or len(row) < 10:  # Skip empty rows
                        continue
                    
                    # Create grades dictionary (only for valid courses)
                    grades = {}
                    for course_column, grade in zip(course_columns, row[10:]):
                        if grade and grade != '-':
                            # Only add grades for valid courses
                            if course_column not in self.invalid_courses:
                                _, course_code = self.course_validator.parse_course_info(course_column)
                                grades[course_code] = grade
                    
                    student = Student(
                        roll_no=row[1],
                        name=row[2],
                        section=row[3],
                        credit_hours_attempted=int(row[4]) if row[4] else 0,
                        credit_hours_earned=int(row[5]) if row[5] else 0,
                        cgpa=float(row[6]) if row[6] else 0.0,
                        warning_status=int(row[7]) if row[7] else 0,
                        enrollment_status=row[8],
                        specialization=row[9],
                        grades=grades
                    )
                    students.append(student)
            
            logger.info(f"Successfully parsed {len(students)} student records")
            return students
        except Exception as e:
            logger.error(f"Error parsing CSV file: {e}")
            raise
    
    def save_to_database(self, students: List[Student]) -> None:
        """Save the parsed data to SQLite database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for student in students:
                    # Insert student record using your existing schema
                    cursor.execute(INSERT_STUDENT, (
                        student.roll_no,
                        student.name,
                        student.section,
                        student.credit_hours_attempted,
                        student.credit_hours_earned,
                        student.cgpa,
                        student.warning_status,
                        student.enrollment_status,
                        student.specialization
                    ))
                    
                    # Insert grade records
                    student_id = cursor.lastrowid
                    grade_records = [
                        (student_id, course_code, grade)
                        for course_code, grade in student.grades.items()
                    ]
                    
                    if grade_records:
                        cursor.executemany('''
                            INSERT INTO grades (student_id, course_code, grade)
                            VALUES (?, ?, ?)
                        ''', grade_records)
                
                conn.commit()
                logger.info("Successfully saved all records to database")
        except sqlite3.Error as e:
            logger.error(f"Error saving to database: {e}")
            raise

if __name__ == "__main__":
    """Main function to run the grade parser."""
    try:
        # Initialize parser
        parser = GradeParser()
        
        # Parse CSV file
        csv_path = Path("grade.csv")
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        students = parser.parse_csv(str(csv_path))
        
        # Check if there were any invalid courses
        if parser.invalid_courses:
            logger.warning("\nWarning: Some courses were not found in the database:")
            for course, error in parser.invalid_courses.items():
                logger.warning(f"  - {course}: {error}")
            
            # You might want to prompt the user here
            response = input("\nDo you want to continue with the valid courses only? (y/n): ")
            if response.lower() != 'y':
                logger.info("Operation cancelled by user")
                exit(0)
        
        # Save to database
        parser.save_to_database(students)
        
        logger.info("Grade parsing and database creation completed successfully")
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise
