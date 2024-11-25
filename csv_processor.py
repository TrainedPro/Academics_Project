import csv
import logging
from typing import List, Tuple
from prospectus_processor import CourseProcessor, Course

from constants.database.config import DB_NAME


class CSVProcessor:
    def __init__(self, csv_path: str, db_path: str):
        self.csv_path = csv_path
        self.processor = CourseProcessor(pdf_path=None)  # Initialize the CourseProcessor
        self.processor.db_path = db_path  # Set the database path
        self.logger = logging.getLogger(__name__)

    def parse_csv(self) -> List[Tuple[Course, str, int]]:
        """
        Parses the CSV file and prepares the courses list using append_courses_and_labs.
        """
        courses = []

        with open(self.csv_path, mode="r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                program_name = row["Program"]
                semester = int(row["Semester"])
                course_code = row["Course Code"]
                course_title = row["Course Title"]

                # Parse credit hours
                credit_hours_class, credit_hours_lab = map(int, row["Credits (Theory + Lab)"].split("+"))

                # Handle prerequisite
                prereq = row["Prerequisite"] if row["Prerequisite"] != "None" else None

                # Use append_courses_and_labs from CourseProcessor
                print(
                    # courses,
                    course_code,
                    course_title,
                    credit_hours_class,
                    credit_hours_lab,
                    prereq,
                    program_name,
                    semester,
                )
                CourseProcessor.append_courses_and_labs(
                    courses,
                    course_code.strip(),
                    course_title.strip(),
                    credit_hours_class,
                    credit_hours_lab,
                    prereq.strip() if prereq else prereq,
                    program_name.strip(),
                    semester,
                )

        self.logger.info(f"Parsed {len(courses)} courses from CSV.")
        return courses

    def insert_csv_data(self):
        """
        Parses the CSV and delegates the insertion to CourseProcessor's insert_courses.
        """
        try:
            courses = self.parse_csv()
            self.processor.insert_courses(courses)  # Leverage existing logic for database insertion
            self.logger.info("CSV data successfully inserted into the database.")
        except Exception as e:
            self.logger.error(f"Failed to insert CSV data: {e}")
            raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("csv_processor.log"),
            logging.StreamHandler(),
        ],
    )

    # Define the paths for the CSV file and the database
    csv_path = "data.csv"  # Replace with the actual path to your CSV file
    db_path = DB_NAME  # Replace with the actual path to your database

    # Initialize and process the CSV
    processor = CSVProcessor(csv_path, db_path)
    processor.insert_csv_data()
