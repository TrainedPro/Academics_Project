import csv
import logging

class CourseModel:
    """
    CourseModel handles the loading of course data from a CSV file and provides functionality
    to filter courses based on user input criteria.
    """

    def __init__(self, csv_file: str):
        """
        Initializes the CourseModel with the path to the CSV file and loads the data.
        
        Args:
            csv_file (str): Path to the CSV file containing course data.
        """
        self.csv_file = csv_file
        self.data = []
        self.load_data()

    def load_data(self):
        """
        Loads course data from the CSV file into the model's data attribute.
        
        Raises:
            FileNotFoundError: If the CSV file does not exist.
            Exception: For other unforeseen errors.
        """
        try:
            with open(self.csv_file, mode='r') as file:
                reader = csv.DictReader(file)
                self.data = list(reader)
            logging.info(f"Data successfully loaded from {self.csv_file}.")
        except FileNotFoundError:
            logging.error(f"The file {self.csv_file} was not found.")
            raise
        except Exception as e:
            logging.error(f"An error occurred while loading data: {e}")
            raise

    def filter_courses(self, batch: str, program: str, semester_type: str) -> list:
        """
        Filters the course data based on batch, program, and semester type.

        Args:
            batch (str): The batch to filter courses by.
            program (str): The program to filter courses by.
            semester_type (str): The type of semester to filter courses by ('1', '2', or '3').

        Returns:
            list: A list of dictionaries containing filtered course information.
        """
        filtered_courses = [
            {
                'Semester': row['Semester'],
                'Course Code': row['Course Code'],
                'Course Title': row['Course Title'],
                'Credits': row['Credits (Theory + Lab)'],
                'Prerequisite': row['Prerequisite']
            }
            for row in self.data
            if row['Batch'] == batch and row['Program'] == program and (
                semester_type == '1' and int(row['Semester']) % 2 == 0 or
                semester_type == '2' and int(row['Semester']) % 2 != 0 or
                semester_type not in ['1', '2']
            )
        ]
        logging.info(f"Filtered {len(filtered_courses)} courses based on provided criteria.")
        return filtered_courses


class CourseView:
    """
    CourseView handles user interaction, including input collection and displaying course information.
    """

    def get_user_input(self) -> tuple:
        """
        Collects user input for batch, program, and semester type.

        Returns:
            tuple: A tuple containing batch, program, and semester type.
        """
        batch = input('Enter Batch: ').strip()
        program = input('Enter Program: ').strip().upper()
        logging.info(f"User entered batch: {batch}, program: {program}")

        print('Choose an option:')
        print('1. Spring Semesters')
        print('2. Fall Semesters')
        print('3. All Semesters')
        semester_type = input('Enter your choice (1/2/3): ').strip()

        match semester_type:
            case '1':
                print('Showing courses for Spring semesters:')
            case '2':
                print('Showing courses for Fall semesters:')
            case '3':
                print('Showing courses for all semesters:')
            case _:
                print('Incorrect Selection!')
                logging.warning('User made an incorrect selection.')
                exit(0)

        return batch, program, semester_type

    def display_courses(self, courses: list):
        """
        Displays the list of courses to the user.

        Args:
            courses (list): A list of dictionaries containing course information.
        """
        if not courses:
            print('No courses found for the given batch, program, and semester type.')
            logging.info('No courses found for the given criteria.')
            return
        
        for course in courses:
            print(f'Semester: {course["Semester"]}')
            print(f'Course Code: {course["Course Code"]}')
            print(f'Course Title: {course["Course Title"]}')
            print(f'Credits: {course["Credits"]}')
            print(f'Prerequisite: {course["Prerequisite"]}')
            print('-' * 40)
        logging.info('Courses displayed successfully.')


class CourseController:
    """
    CourseController manages the interaction between the model and the view.
    """

    def __init__(self, model: CourseModel, view: CourseView):
        """
        Initializes the CourseController with a model and a view.

        Args:
            model (CourseModel): An instance of CourseModel.
            view (CourseView): An instance of CourseView.
        """
        self.model = model
        self.view = view

    def run(self):
        """
        Executes the main workflow of the application.
        """
        batch, program, semester_type = self.view.get_user_input()
        courses = self.model.filter_courses(batch, program, semester_type)
        self.view.display_courses(courses)


if __name__ == '__main__':
    # Set up logging configuration
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        model = CourseModel('data.csv')
        view = CourseView()
        controller = CourseController(model, view)
        controller.run()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        exit(1)
