import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import csv

# Database connection helper
def connect_db():
    return sqlite3.connect('project.sqlite3')

# Fetch courses based on program and semester
def fetch_courses_by_program_and_semester(program, semester):
    conn = connect_db()
    cursor = conn.cursor()
    query = '''
    SELECT c.course_title
    FROM program_courses pc
    JOIN courses c ON pc.course_code = c.course_code
    WHERE pc.program_name = ? AND pc.semester = ?;
    '''
    cursor.execute(query, (program, semester))
    courses = cursor.fetchall()
    conn.close()
    return [course[0] for course in courses]

# Get prerequisite course code for a given course name
def get_prerequisite(course_name):
    conn = connect_db()
    cursor = conn.cursor()
    query = '''
    SELECT prerequisite_course_code
    FROM courses
    WHERE course_title = ?;
    '''
    cursor.execute(query, (course_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Get eligible students for a course
def get_eligible_students(course_name):
    conn = connect_db()
    cursor = conn.cursor()
    prerequisite = get_prerequisite(course_name)
    if prerequisite:
        query = '''
        SELECT s.name
        FROM students s
        JOIN grades g ON s.roll_no = g.roll_no
        JOIN courses c ON g.course_code = c.course_code
        WHERE c.course_title = ? AND g.grade  IN ('-', 'F', 'W', 'I')
        AND EXISTS (
            SELECT 1
            FROM courses p
            WHERE p.course_code = ? AND p.course_code = c.prerequisite_course_code
        );
        '''
        cursor.execute(query, (course_name, prerequisite))
        students = cursor.fetchall()
        conn.close()
        return [student[0] for student in students], len(students)
    conn.close()
    return [], 0

# Insert a course into the database
def insert_course(course_code, course_title, credit_hours, prerequisite):
    conn = connect_db()
    cursor = conn.cursor()
    query = '''
    INSERT OR IGNORE INTO courses (course_code, course_title, credit_hours, prerequisite_course_code)
    VALUES (?, ?, ?, ?);
    '''
    cursor.execute(query, (course_code, course_title, credit_hours, prerequisite))
    conn.commit()
    conn.close()

# Export to CSV helper
def export_to_csv(filename, header, rows):
    if rows:
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)
        messagebox.showinfo("Success", f"Data exported to '{filename}'")
    else:
        messagebox.showinfo("No Data", "No data to export.")

# Scrollable frame for dynamic pages
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
class BatchAdvisorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fast Batch Advisor Automation")
        self.root.geometry("800x600")  # Adjust window size

        # Create a main container with two frames: side menu and main content
        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True)

        # Left-hand side menu
        self.side_menu = ttk.Frame(main_frame, width=220)
        self.side_menu.pack(side="left", fill="y")

        # Main content area
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side="left", fill="both", expand=True)

        # Add a notebook for the main content area
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill="both", expand=True)

        self.add_side_menu_buttons()
        self.create_main_menu()
        self.create_show_courses_page()
        self.create_show_eligible_students_page()
        self.create_add_course_page()

    def add_side_menu_buttons(self):
        # Buttons for navigation in the side menu
        buttons = [
            ("Main Menu", self.notebook.select, 0),
            ("Show Courses", self.notebook.select, 1),
            ("Show Eligible Students", self.notebook.select, 2),
            ("Add Course", self.notebook.select, 3),
        ]
        for idx, (text, command, page) in enumerate(buttons):
            btn = tk.Button(
                self.side_menu,
                text=text,
                font=("Arial", 14),
                width=18,
                height=2,  # Larger buttons for a cleaner look
                bg="#4CAF50",
                fg="white",
                command=lambda p=page: command(p),
            )
            btn.pack(pady=5)  # Spacing between buttons

    def create_main_menu(self):
        main_menu_page = ttk.Frame(self.notebook)
        self.notebook.add(main_menu_page, text="Main Menu")

        # Background Image
        image = Image.open("pictures/f.png")
        background_image = ImageTk.PhotoImage(image)
        background_label = tk.Label(main_menu_page, image=background_image)
        background_label.image = background_image
        background_label.place(relwidth=1, relheight=1)

        heading_label = tk.Label(main_menu_page, text="Fast Batch Advisor Automation",
                                 font=("Arial", 18, "bold"), bg="#FF5733", fg="white", width=40)
        heading_label.pack(pady=20)

    def create_show_courses_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="Show Courses")

        program_label = tk.Label(page, text="Program Name:", font=("Arial", 12))
        program_label.pack(pady=10)
        program_entry = tk.Entry(page, font=("Arial", 12))
        program_entry.pack(pady=5)

        semester_label = tk.Label(page, text="Semester:", font=("Arial", 12))
        semester_label.pack(pady=10)
        semester_entry = tk.Entry(page, font=("Arial", 12))
        semester_entry.pack(pady=5)

        courses_label = tk.Label(page, text="", font=("Arial", 12))
        courses_label.pack(pady=10)

        def show_courses():
            program = program_entry.get()
            semester = semester_entry.get()
            if not program or not semester:
                messagebox.showerror("Input Error", "Please enter all fields.")
                return
            courses = fetch_courses_by_program_and_semester(program, semester)
            courses_label.config(text="\n".join(courses) if courses else "No courses found.")
            export_to_csv("courses.csv", ["Course Title"], [(course,) for course in courses])

        show_button = tk.Button(page, text="Show Courses", font=("Arial", 12), command=show_courses)
        show_button.pack(pady=10)

    def create_show_eligible_students_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="Show Eligible Students")

        course_label = tk.Label(page, text="Course Name:", font=("Arial", 12))
        course_label.pack(pady=10)
        course_entry = tk.Entry(page, font=("Arial", 12))
        course_entry.pack(pady=5)

        result_label = tk.Label(page, text="", font=("Arial", 12))
        result_label.pack(pady=10)

        def show_students():
            course = course_entry.get()
            if not course:
                messagebox.showerror("Input Error", "Please enter the course name.")
                return
            students, count = get_eligible_students(course)
            result_label.config(text=f"Eligible Students ({count}):\n" + "\n".join(students))
            export_to_csv("eligible_students.csv", ["Student Name"], [(student,) for student in students])

        show_button = tk.Button(page, text="Show Eligible Students", font=("Arial", 12),
                                command=show_students)
        show_button.pack(pady=10)

    def create_add_course_page(self):
        page = ttk.Frame(self.notebook)
        self.notebook.add(page, text="Add Course")

        labels = ["Course Code:", "Course Title:", "Credit Hours:", "Prerequisite Course Code:"]
        entries = []
        for label_text in labels:
            label = tk.Label(page, text=label_text, font=("Arial", 12))
            label.pack(pady=10)
            entry = tk.Entry(page, font=("Arial", 12))
            entry.pack(pady=5)
            entries.append(entry)

        def add_course():
            course_code, title, hours, prereq = [e.get() for e in entries]
            if not course_code or not title or not hours:
                messagebox.showerror("Input Error", "Please fill in all required fields.")
                return
            insert_course(course_code, title, hours, prereq)
            messagebox.showinfo("Success", f"Course '{title}' added successfully.")

        add_button = tk.Button(page, text="Add Course", font=("Arial", 12), command=add_course)
        add_button.pack(pady=10)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = BatchAdvisorApp(root)
    root.mainloop()
