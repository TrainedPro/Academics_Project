import fitz  # PyMuPDF
import logging
from typing import List, Tuple
import csv

class CourseModel:
    def __init__(self, pdf_path: str, program_name: str):
        self.pdf_path = pdf_path
        self.program_name = program_name
        self.search_term = f"Tentative Study Plan-Bachelor of Science ({program_name})"
        self.logger = logging.getLogger(__name__)

    def find_page_text(self) -> str:
        """
        Searches for a page containing the search term in the PDF and returns its text.

        Returns:
            str: The text content of the page containing the search term.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            ValueError: If the search term is not found in any page.
            Exception: For other unforeseen errors.
        """
        try:
            with fitz.open(self.pdf_path) as doc:
                for page_number in range(len(doc)):
                    page = doc.load_page(page_number)
                    text = page.get_text()

                    if self.search_term in text:
                        self.logger.debug(f"Search term found on page {page_number + 1}.")
                        return text

                raise ValueError(f"Search term '{self.search_term}' not found in the document.")

        except FileNotFoundError:
            self.logger.error(f"The file '{self.pdf_path}' was not found.")
            raise
        except Exception as e:
            self.logger.error(f"An error occurred while processing the PDF: {e}")
            raise

    def parse_course_info(self, text: str) -> List[Tuple[str, int, str, str, int, int, str]]:
        """
        Parses the course information from the extracted text.

        Args:
            text (str): The text extracted from the PDF containing course information.

        Returns:
            List[Tuple[str, int, str, str, int, int, str]]: A list of tuples with course details.
        """
        lines = [x.strip() for x in text.split('\n')]
        courses = []
        
        idx = 0
        while 'Semester-I' not in lines[idx]:
            idx += 1

        semester = 0 # can also be calculated through `total_count`
        total_count = 0
        while idx < len(lines) - 1:
            if 'Total' in lines[idx]:
                idx += 3
                total_count += 1

                if total_count >= 8:
                    break

            elif 'Semester-' in lines[idx]:
                semester += 1
                idx += 1

            else:
                course_code = lines[idx]
                idx += 1

                while course_code[-1] == '/':
                    course_code += lines[idx]
                    idx += 1

                course_title = lines[idx]
                idx += 1

                while not lines[idx].isdigit():
                    course_title += ' ' + lines[idx]
                    idx += 1

                credit_hours_class = int(lines[idx])
                idx += 1

                credit_hours_lab = int(lines[idx])
                idx += 1

                prereq = lines[idx]
                idx += 1

                if prereq == '—':
                    prereq = ''

                self.logger.debug(msg=[
                    idx,
                    self.program_name,
                    semester,
                    course_code,
                    course_title,
                    credit_hours_class,
                    credit_hours_lab,
                    prereq]
                )

                courses.append((
                    self.program_name,
                    semester,
                    course_code,
                    course_title,
                    credit_hours_class,
                    credit_hours_lab,
                    prereq
                ))

        return courses

class CourseView:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def write_courses_to_csv(self, courses: List[Tuple[str, int, str, str, int, int, str]], filename: str):
        """
        Writes the course information to a CSV file.

        Args:
            courses (List[Tuple[str, int, str, str, int, int, str]]): The list of course information tuples.
            filename (str): The name of the CSV file to write.
        """
        try:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Program Name', 'Semester', 'Course Code', 'Course Title', 'Credit Hours (Class)', 'Credit Hours (Lab)', 'Pre-requisites'])
                for course in courses:
                    writer.writerow(course)
            self.logger.info(f"Course information has been written to {filename}.")
        except Exception as e:
            self.logger.error(f"An error occurred while writing to CSV: {e}")


class CourseController:
    def __init__(self, model: CourseModel, view: CourseView):
        self.model = model
        self.view = view
        self.logger = logging.getLogger(__name__)

    def execute(self):
        try:
            # Find and extract the text from the page containing the study plan
            page_text = self.model.find_page_text()

            # Parse the extracted text to get course information
            courses = self.model.parse_course_info(page_text)

            # Print the parsed courses for verification
            self.logger.debug(f"Parsed courses: {courses}")

            # Write the course information to a CSV file
            csv_filename = f"_{self.model.program_name.replace(' ', '_')}_Courses.csv"
            self.view.write_courses_to_csv(courses, csv_filename)

        except Exception as error:
            self.logger.error(f"Failed to extract and process text: {error}")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Set up logging configuration
    for program in ["Artificial Intelligence", "Computer Science", "Cyber Security", "Data Science", "Software Engineering"]:
        model = CourseModel(pdf_path="Computing Programs.pdf", program_name=program)
        view = CourseView()
        controller = CourseController(model=model, view=view)
        controller.execute()