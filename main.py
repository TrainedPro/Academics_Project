import csv

class CourseModel:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.data = []
        self.load_data()

    def load_data(self):
        with open(self.csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            self.data = list(reader)

    def filter_courses(self, batch, program):
        return [
            {
                "Course Code": row["Course Code"],
                "Course Title": row["Course Title"],
                "Credits": row["Credits (Theory + Lab)"],
                "Prerequisite": row["Prerequisite"]
            }
            for row in self.data
            if row["Batch"] == batch and row["Program"] == program
        ]

class CourseView:
    def get_user_input(self):
        batch = input("Enter Batch: ")
        program = input("Enter Program: ")
        return batch, program

    def display_courses(self, courses):
        if not courses:
            print("No courses found for the given batch and program.")
        else:
            for course in courses:
                print(f"Course Code: {course['Course Code']}")
                print(f"Course Title: {course['Course Title']}")
                print(f"Credits: {course['Credits']}")
                print(f"Prerequisite: {course['Prerequisite']}")
                print("-" * 40)

class CourseController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def run(self):
        batch, program = self.view.get_user_input()
        courses = self.model.filter_courses(batch, program)
        self.view.display_courses(courses)

if __name__ == "__main__":
    model = CourseModel("data.csv")
    view = CourseView()
    controller = CourseController(model, view)
    controller.run()
