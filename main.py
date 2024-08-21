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

    def filter_courses(self, batch, program, semester_type):
        if semester_type == "1":
            # Spring Semesters (Even)
            return [
                {
                    "Course Code": row["Course Code"],
                    "Course Title": row["Course Title"],
                    "Credits": row["Credits (Theory + Lab)"],
                    "Prerequisite": row["Prerequisite"],
                    "Semester": row["Semester"]
                }
                for row in self.data
                if row["Batch"] == batch and row["Program"] == program and int(row["Semester"]) % 2 == 0
            ]
        elif semester_type == "2":
            # Fall Semesters (Odd)
            return [
                {
                    "Course Code": row["Course Code"],
                    "Course Title": row["Course Title"],
                    "Credits": row["Credits (Theory + Lab)"],
                    "Prerequisite": row["Prerequisite"],
                    "Semester": row["Semester"]
                }
                for row in self.data
                if row["Batch"] == batch and row["Program"] == program and int(row["Semester"]) % 2 != 0
            ]
        else:
            # All Semesters
            return [
                {
                    "Course Code": row["Course Code"],
                    "Course Title": row["Course Title"],
                    "Credits": row["Credits (Theory + Lab)"],
                    "Prerequisite": row["Prerequisite"],
                    "Semester": row["Semester"]
                }
                for row in self.data
                if row["Batch"] == batch and row["Program"] == program
            ]

class CourseView:
    def get_user_input(self):
        batch = input("Enter Batch: ")
        program = input("Enter Program: ")
        print("Choose an option:")
        print("1. Spring Semesters")
        print("2. Fall Semesters")
        print("3. All Semesters")
        semester_type = input("Enter your choice (1/2/3): ")
        return batch, program, semester_type

    def display_courses(self, courses, semester_type):
        if not courses:
            print("No courses found for the given batch, program, and semester type.")
        else:
            if semester_type == "1":
                print("Showing courses for Spring semesters:")
            elif semester_type == "2":
                print("Showing courses for Fall semesters:")
            else:
                print("Showing courses for all semesters:")

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
        batch, program, semester_type = self.view.get_user_input()
        courses = self.model.filter_courses(batch, program, semester_type)
        self.view.display_courses(courses, semester_type)

if __name__ == "__main__":
    model = CourseModel("data.csv")
    view = CourseView()
    controller = CourseController(model, view)
    controller.run()
