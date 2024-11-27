import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import database
import utils
from utils import show_courses, add_course_to_program, remove_course_from_program, fetch_courses_from_db, populate_course_dropdown

class ScrollableFrame(ttk.Frame):
    """A scrollable frame for better UI layout."""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=560)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=20)
        self.scrollbar.pack(side="right", fill="y")

def create_sidebar_buttons(sidebar_frame, notebook, button_style):
    """Create sidebar buttons for navigation."""
    show_courses_button = tk.Button(
        sidebar_frame, 
        text="Show Courses", 
        command=lambda: notebook.select(notebook.tabs()[0]), 
        bg="#3498DB",
        activebackground="#2980B9",
        **button_style
    )
    show_courses_button.pack(pady=10, padx=10)

    show_eligible_button = tk.Button(
        sidebar_frame, 
        text="Show Eligible Students", 
        command=lambda: notebook.select(notebook.tabs()[1]), 
        bg="#E74C3C",
        activebackground="#C0392B",
        **button_style
    )
    show_eligible_button.pack(pady=10, padx=10)

    add_course_button = tk.Button(
        sidebar_frame, 
        text="Add Course", 
        command=lambda: notebook.select(notebook.tabs()[2]), 
        bg="#2ECC71",
        activebackground="#27AE60",
        **button_style
    )
    add_course_button.pack(pady=10, padx=10)

# Rest of the code remains the same, but modify the create_courses_page function:

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import utils  # Make sure the utils module is imported correctly

def create_courses_page(notebook, program_options, semester_options):
    """Create the Show Courses page with a table view."""
    courses_page = ttk.Frame(notebook)
    
    # Program Dropdown
    program_frame = tk.Frame(courses_page)
    program_frame.pack(pady=10)

    program_name_label = tk.Label(program_frame, text="Select Program:", font=("Arial", 12))
    program_name_label.pack(side=tk.LEFT, padx=5)

    program_var = tk.StringVar()
    program_dropdown = ttk.Combobox(
        program_frame, 
        textvariable=program_var, 
        values=program_options, 
        width=30, 
        state="readonly"
    )
    program_dropdown.pack(side=tk.LEFT, padx=5)

    # Semester Dropdown
    semester_frame = tk.Frame(courses_page)
    semester_frame.pack(pady=10)

    semester_label = tk.Label(semester_frame, text="Select Semester:", font=("Arial", 12))
    semester_label.pack(side=tk.LEFT, padx=5)

    semester_var = tk.StringVar()
    semester_dropdown = ttk.Combobox(
        semester_frame, 
        textvariable=semester_var, 
        values=semester_options, 
        width=30, 
        state="readonly"
    )
    semester_dropdown.pack(side=tk.LEFT, padx=5)

    # Courses Treeview
    courses_tree = ttk.Treeview(courses_page, columns=("Course Code", "Course Title", "Credit Hours"), show="headings")
    courses_tree.heading("Course Code", text="Course Code")
    courses_tree.heading("Course Title", text="Course Title")
    courses_tree.heading("Credit Hours", text="Credit Hours")
    
    # Set column widths
    courses_tree.column("Course Code", width=100, anchor="center")
    courses_tree.column("Course Title", width=300)
    courses_tree.column("Credit Hours", width=100, anchor="center")
    
    courses_tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    # Scrollbar for Treeview
    scrollbar = ttk.Scrollbar(courses_page, orient=tk.VERTICAL, command=courses_tree.yview)
    courses_tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Fetch available courses from the database and populate the course dropdown
    courses = fetch_courses_from_db()
    course_var = tk.StringVar()
    course_dropdown = ttk.Combobox(courses_page, textvariable=course_var, values=[], width=30, state="readonly")
    course_dropdown.set("Select Course")
    course_dropdown.pack(pady=10)
    
    # Populate course dropdown with course titles
    course_titles = populate_course_dropdown(courses, course_var)
    course_dropdown['values'] = course_titles

    # Show Courses Button
    show_courses_button = tk.Button(
        courses_page, 
        text="Show Courses", 
        command=lambda: show_courses(program_var, semester_var, courses_tree), 
        font=("Arial", 12)
    )
    show_courses_button.pack(pady=10)

    # Add Course Button
    add_course_button = tk.Button(
        courses_page, 
        text="Add Course", 
        command=lambda: add_course_to_program(course_var, program_var, semester_var, courses_tree), 
        font=("Arial", 12)
    )
    add_course_button.pack(pady=10)

    # Remove Course Button
    remove_course_button = tk.Button(
        courses_page, 
        text="Remove Course", 
        command=lambda: remove_course_from_program(program_var, semester_var, courses_tree), 
        font=("Arial", 12)
    )
    remove_course_button.pack(pady=10)

    return courses_page

def add_course_to_table(courses_tree):
    """Add a new course to the courses table."""
    # Prompt for course details
    course_code = simpledialog.askstring("Input", "Enter Course Code:")
    course_title = simpledialog.askstring("Input", "Enter Course Title:")
    credit_hours = simpledialog.askstring("Input", "Enter Credit Hours:")
    
    # Validation (ensure all fields are provided)
    if not course_code or not course_title or not credit_hours:
        messagebox.showerror("Input Error", "Please provide all course details.")
        return

    # Add to the table
    courses_tree.insert("", "end", values=(course_code, course_title, credit_hours))
    messagebox.showinfo("Success", f"Course '{course_title}' added successfully!")

def remove_course_from_table(courses_tree):
    """Remove the selected course from the table."""
    selected_item = courses_tree.selection()
    
    if not selected_item:
        messagebox.showerror("Selection Error", "Please select a course to remove.")
        return

    # Remove selected course from the table
    courses_tree.delete(selected_item)
    messagebox.showinfo("Success", "Selected course removed successfully!")


import tkinter as tk
import tkinter.ttk as ttk
import database

import tkinter as tk
import tkinter.ttk as ttk
import database

import tkinter as tk
import tkinter.ttk as ttk
import database

def create_eligible_students_page(notebook, course_options=None):
    """Create the Show Eligible Students page dynamically."""
    eligible_page = ttk.Frame(notebook)
    scrollable_eligible = ScrollableFrame(eligible_page)
    scrollable_eligible.pack(fill="both", expand=True)

    def create_dynamic_eligible_page():
        # Clear existing widgets
        for widget in scrollable_eligible.scrollable_frame.winfo_children():
            widget.destroy()

        # Dynamically fetch course options from database
        conn = database.connect_database('project.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT course_code, course_title FROM courses")
        course_data = cursor.fetchall()
        conn.close()

        # Create course options with both code and title
        course_options_dynamic = [f"{course[0]} - {course[1]}" for course in course_data]

        # Use passed course_options if provided, otherwise use dynamically fetched options
        final_course_options = course_options if course_options is not None else course_options_dynamic

        # Course Name Dropdown
        course_name_label = tk.Label(
            scrollable_eligible.scrollable_frame, 
            text="Select Course Name:", 
            font=("Arial", 12)
        )
        course_name_label.pack(pady=10)

        course_name_var = tk.StringVar()
        course_name_dropdown = ttk.Combobox(
            scrollable_eligible.scrollable_frame, 
            textvariable=course_name_var, 
            values=final_course_options, 
            width=50, 
            state="readonly"
        )
        course_name_dropdown.pack(pady=5)
        course_name_dropdown.set("Select Course")

        # Result Label
        result_label = tk.Label(
            scrollable_eligible.scrollable_frame, 
            text="", 
            font=("Arial", 12), 
            justify="left"
        )
        result_label.pack(pady=20)

        # Show Eligible Students Button
        show_eligible_button = tk.Button(
            scrollable_eligible.scrollable_frame, 
            text="Show Eligible Students", 
            command=lambda: utils.show_eligible_students(course_name_var, result_label), 
            font=("Arial", 12)
        )
        show_eligible_button.pack(pady=10)

        # Refresh Button
        refresh_button = tk.Button(
            scrollable_eligible.scrollable_frame,
            text="Refresh Courses",
            command=create_dynamic_eligible_page,
            font=("Arial", 12),
            bg="#3498DB",
            activebackground="#2980B9"
        )
        refresh_button.pack(pady=5)

    # Initial creation of dynamic page
    create_dynamic_eligible_page()

    return eligible_page
def create_add_course_page(notebook):
    """Create the Add Course page."""
    add_course_page = ttk.Frame(notebook)
    scrollable_add_course = ScrollableFrame(add_course_page)
    scrollable_add_course.pack(fill="both", expand=True)

    # Course Code Entry
    course_code_var = tk.StringVar()
    course_code_entry = utils.create_labeled_entry(
        scrollable_add_course.scrollable_frame, 
        "Enter Course Code:", 
        course_code_var
    )

    # Course Title Entry
    course_title_var = tk.StringVar()
    course_title_entry = utils.create_labeled_entry(
        scrollable_add_course.scrollable_frame, 
        "Enter Course Title:", 
        course_title_var
    )

    # Credit Hours Entry
    credit_hours_var = tk.StringVar()
    credit_hours_entry = utils.create_labeled_entry(
        scrollable_add_course.scrollable_frame, 
        "Enter Credit Hours:", 
        credit_hours_var
    )

    # Prerequisite Course Code Entry
    prerequisite_course_code_var = tk.StringVar()
    prerequisite_course_code_entry = utils.create_labeled_entry(
        scrollable_add_course.scrollable_frame, 
        "Enter Prerequisite Course Code (Optional):", 
        prerequisite_course_code_var
    )

    # Add Course Button
    add_course_button = tk.Button(
        scrollable_add_course.scrollable_frame, 
        text="Add Course", 
        command=lambda: utils.add_course(
            course_code_var, 
            course_title_var, 
            credit_hours_var, 
            prerequisite_course_code_var
        ), 
        font=("Arial", 12)
    )
    add_course_button.pack(pady=10)

    # Footer
    footer_label = tk.Label(
        scrollable_add_course.scrollable_frame, 
        text="Fast Batch Advisor Automation System", 
        font=("Arial", 10), 
        fg="gray"
    )
    footer_label.pack(pady=20)

    return add_course_page
import tkinter as tk
from tkinter import ttk
import database  # Assuming this module connects to your database
import utils  # Assuming utility functions like 'create_labeled_dropdown' are in this module

import tkinter as tk
import tkinter.ttk as ttk
import database

def create_manage_grades_page(notebook):
    """Create the Manage Grades page for submitting grades dynamically."""

    manage_grades_page = ttk.Frame(notebook)
    scrollable_grades_frame = ScrollableFrame(manage_grades_page)
    scrollable_grades_frame.pack(fill="both", expand=True)

    # Variables to store current data and dropdowns
    roll_no_var = tk.StringVar()
    course_var = tk.StringVar()
    grade_var = tk.StringVar()

    # Create dynamic update mechanism
    def create_dynamic_dropdowns():
        # Clear existing widgets
        for widget in scrollable_grades_frame.scrollable_frame.winfo_children():
            widget.destroy()

        # Fetch current data from database
        conn = database.connect_database('project.sqlite3')
        cursor = conn.cursor()

        # Fetch student roll numbers dynamically
        cursor.execute("SELECT roll_no FROM students")
        roll_numbers = [row[0] for row in cursor.fetchall()]

        # Fetch courses dynamically
        cursor.execute("SELECT course_code, course_title FROM courses")
        courses = cursor.fetchall()
        conn.close()

        # Dynamically create dropdown for Student Roll Numbers
        roll_no_dropdown = ttk.Combobox(
            scrollable_grades_frame.scrollable_frame,
            textvariable=roll_no_var,
            values=roll_numbers,
            width=50,
            state="readonly"
        )
        utils.create_labeled_dropdown(
            scrollable_grades_frame.scrollable_frame,
            "Select Student Roll No:",
            roll_no_dropdown
        )

        # Dynamically create dropdown for courses
        course_options = [f"{course[0]} - {course[1]}" for course in courses]
        course_dropdown = ttk.Combobox(
            scrollable_grades_frame.scrollable_frame,
            textvariable=course_var,
            values=course_options,
            width=50,
            state="readonly"
        )
        utils.create_labeled_dropdown(
            scrollable_grades_frame.scrollable_frame,
            "Select Course:",
            course_dropdown
        )

        # Dynamically create dropdown for Grades
        grade_options = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F", "-"]
        grade_dropdown = ttk.Combobox(
            scrollable_grades_frame.scrollable_frame,
            textvariable=grade_var,
            values=grade_options,
            width=50,
            state="readonly"
        )
        grade_dropdown.set("Select Grade")
        utils.create_labeled_dropdown(
            scrollable_grades_frame.scrollable_frame,
            "Select Grade:",
            grade_dropdown
        )

        # Submit Grade Button
        submit_grade_button = tk.Button(
            scrollable_grades_frame.scrollable_frame,
            text="Submit Grade",
            command=lambda: utils.submit_grade(roll_no_var, course_var, grade_var),
            font=("Arial", 12),
            bg="#2ECC71",
            activebackground="#27AE60"
        )
        submit_grade_button.pack(pady=10)

        # Refresh Button
        refresh_button = tk.Button(
            scrollable_grades_frame.scrollable_frame,
            text="Refresh Data",
            command=create_dynamic_dropdowns,
            font=("Arial", 12),
            bg="#3498DB",
            activebackground="#2980B9"
        )
        refresh_button.pack(pady=5)

        # Footer
        footer_label = tk.Label(
            scrollable_grades_frame.scrollable_frame,
            text="Fast Batch Advisor Automation System",
            font=("Arial", 10),
            fg="gray"
        )
        footer_label.pack(pady=20)

    # Initial creation of dynamic dropdowns
    create_dynamic_dropdowns()

    return manage_grades_page
import tkinter as tk
from tkinter import ttk, messagebox
import utils
import database

def create_teachers_page(notebook):
    """Create the Teachers page for managing teachers and assigning courses."""
    teachers_page = ttk.Frame(notebook)
    scrollable_teachers_frame = ScrollableFrame(teachers_page)
    scrollable_teachers_frame.pack(fill="both", expand=True)

    # Fetch courses from the database
    conn = database.connect_database('project.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT course_code, course_title FROM courses")
    courses = cursor.fetchall()
    conn.close()

    # Create a dropdown for Course selection (course_code)
    course_var = tk.StringVar()
    course_options = [f"{course[0]} - {course[1]}" for course in courses]  # Format as 'code - title'
    course_dropdown = ttk.Combobox(
        scrollable_teachers_frame.scrollable_frame,
        textvariable=course_var,
        values=course_options,
        width=50,
        state="readonly"
    )
    course_dropdown.set("Select Course")
    utils.create_labeled_dropdown(
        scrollable_teachers_frame.scrollable_frame,
        "Select Course:",
        course_dropdown
    )

    # Entry for Credit Hours
    credit_hours_var = tk.StringVar()
    utils.create_labeled_entry(
        scrollable_teachers_frame.scrollable_frame,
        "Enter Credit Hours:",
        credit_hours_var
    )

    # Create a dropdown for Teacher selection (will be refreshed after adding a teacher)
    teacher_var = tk.StringVar()
    teacher_options = []  # Start with an empty list
    teacher_dropdown = ttk.Combobox(
        scrollable_teachers_frame.scrollable_frame,
        textvariable=teacher_var,
        values=teacher_options,
        width=50,
        state="readonly"
    )
    teacher_dropdown.set("Select Teacher")
    utils.create_labeled_dropdown(
        scrollable_teachers_frame.scrollable_frame,
        "Select Teacher:",
        teacher_dropdown
    )

    # Refresh the teacher dropdown with the latest data from the database
    refresh_teacher_dropdown(teacher_dropdown)

    # Assign Course to Teacher Button
    assign_course_button = tk.Button(
        scrollable_teachers_frame.scrollable_frame,
        text="Assign Course to Teacher",
        command=lambda: assign_course_to_teacher(teacher_var, course_var, credit_hours_var, assigned_courses_tree),
        font=("Arial", 12),
        bg="#2ECC71",
        activebackground="#27AE60"
    )
    assign_course_button.pack(pady=10)

    # Add Teacher Form (name and specialty dropdown)
    teacher_name_var = tk.StringVar()
    specialty_var = tk.StringVar()

    utils.create_labeled_entry(
        scrollable_teachers_frame.scrollable_frame,
        "Enter Teacher Name:",
        teacher_name_var
    )

    # Teacher Specialty Dropdown (courses)
    specialty_dropdown = ttk.Combobox(
        scrollable_teachers_frame.scrollable_frame,
        textvariable=specialty_var,
        values=[f"{course[0]} - {course[1]}" for course in courses],
        state="readonly",
        width=50
    )
    specialty_dropdown.set("Select Specialty (Course)")
    utils.create_labeled_dropdown(
        scrollable_teachers_frame.scrollable_frame,
        "Select Specialty (Course):",
        specialty_dropdown
    )

    # Add Teacher Button
    add_teacher_button = tk.Button(
        scrollable_teachers_frame.scrollable_frame,
        text="Add Teacher",
        command=lambda: add_teacher_and_refresh(teacher_name_var, specialty_var, teacher_dropdown),
        font=("Arial", 12),
        bg="#2ECC71",
        activebackground="#27AE60"
    )
    add_teacher_button.pack(pady=10)

    # Assigned Courses List Table (showing teacher, course, and credit hours)
    assigned_courses_tree = ttk.Treeview(
        scrollable_teachers_frame.scrollable_frame, 
        columns=("Teacher Name", "Course Code", "Course Title", "Credit Hours"), 
        show="headings"
    )
    assigned_courses_tree.heading("Teacher Name", text="Teacher Name")
    assigned_courses_tree.heading("Course Code", text="Course Code")
    assigned_courses_tree.heading("Course Title", text="Course Title")
    assigned_courses_tree.heading("Credit Hours", text="Credit Hours")
    assigned_courses_tree.column("Teacher Name", width=200)
    assigned_courses_tree.column("Course Code", width=100)
    assigned_courses_tree.column("Course Title", width=200)
    assigned_courses_tree.column("Credit Hours", width=100)
    assigned_courses_tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    # Fetch the list of teachers with their assigned courses
    refresh_assigned_courses_table(assigned_courses_tree)

    return teachers_page


def add_teacher_and_refresh(teacher_name_var, specialty_var, teacher_dropdown):
    """Add a new teacher and refresh the teacher dropdown."""
    teacher_name = teacher_name_var.get()
    specialty = specialty_var.get()  # specialty corresponds to course_code

    if not teacher_name or not specialty:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    try:
        # Add teacher to the database
        conn = database.connect_database('project.sqlite3')
        cursor = conn.cursor()
        query = '''
        INSERT INTO teachers (name, specialty)
        VALUES (?, ?)
        '''
        cursor.execute(query, (teacher_name, specialty))  # specialty is the course_code
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Teacher '{teacher_name}' added successfully!")
        
        # Clear the form fields after submission
        teacher_name_var.set('')
        specialty_var.set('')

        # Refresh the teacher dropdown
        refresh_teacher_dropdown(teacher_dropdown)
        
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")


def refresh_teacher_dropdown(teacher_dropdown):
    """Refresh the teacher dropdown list with updated data from the database."""
    conn = database.connect_database('project.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM teachers")
    teachers = cursor.fetchall()
    conn.close()
    
    teacher_options = [teacher[0] for teacher in teachers]
    teacher_dropdown['values'] = teacher_options
    if teacher_options:
        teacher_dropdown.set(teacher_options[-1])  # Set to the latest added teacher
    else:
        teacher_dropdown.set("Select Teacher")


def refresh_assigned_courses_table(assigned_courses_tree):
    """Fetch and refresh the table with teacher-course assignments (including credit hours)."""
    # Clear existing entries
    for row in assigned_courses_tree.get_children():
        assigned_courses_tree.delete(row)

    try:
        # Fetch teacher-course assignments with credit hours from the teacher_courses table
        conn = database.connect_database('project.sqlite3')
        cursor = conn.cursor()

        # Query to get teacher name, course code, course title, and credit hours
        cursor.execute("""
            SELECT t.name, c.course_code, c.course_title, tc.credit_hours
            FROM teachers t
            JOIN teacher_courses tc ON t.id = tc.teacher_id
            JOIN courses c ON c.course_code = tc.course_code
        """)
        assigned_courses = cursor.fetchall()
        conn.close()

        # Insert the data into the table
        for row in assigned_courses:
            assigned_courses_tree.insert("", "end", values=row)  # Insert teacher's name, course info, and credit hours

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

def assign_course_to_teacher(teacher_name_var, course_var, credit_hours_var, assigned_courses_tree):
    """Assign the selected course and credit hours to the selected teacher."""
    teacher_name = teacher_name_var.get()
    course_info = course_var.get()
    credit_hours = credit_hours_var.get()

    if not teacher_name or not course_info or not credit_hours:
        messagebox.showerror("Input Error", "Please select both a teacher, a course, and enter credit hours.")
        return

    # Extract the course code from the course_info (e.g., "CS101 - Introduction to CS")
    course_code = course_info.split(" - ")[0]
    course_title = course_info.split(" - ")[1]

    try:
        # Fetch teacher ID from teacher name
        conn = database.connect_database('project.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM teachers WHERE name = ?", (teacher_name,))
        teacher_id = cursor.fetchone()

        if not teacher_id:
            messagebox.showerror("Database Error", "Teacher not found in the database.")
            return

        teacher_id = teacher_id[0]  # Get the teacher ID

        # Insert the course, teacher ID, and credit hours into the teacher_courses table
        query = '''
        INSERT INTO teacher_courses (teacher_id, course_code, credit_hours)
        VALUES (?, ?, ?)
        '''
        cursor.execute(query, (teacher_id, course_code, credit_hours))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Course '{course_code}' successfully assigned to teacher '{teacher_name}' with {credit_hours} credit hours.")

        # Refresh the assigned courses table to display the newly assigned course
        refresh_assigned_courses_table(assigned_courses_tree)

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        
import re

def roll_no_exists(roll_no):
    """
    Check if a roll number already exists in the database.
    
    :param roll_no: Roll number to check
    :return: True if roll number exists, False otherwise
    """
    conn = database.connect_database("project.sqlite3")
    if not conn:
        return False

    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM students WHERE roll_no = ?", (roll_no,))
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.Error as e:
        messagebox.showerror("Database Query Error", str(e))
        return False
    finally:
        conn.close()

def validate_roll_no(roll_no):
    """
    Validate roll number format: xxp-xxxx
    """
    pattern = r'^[1-9]{2}p-\d{4}$'
    return re.match(pattern, roll_no) is not None

def validate_cgpa(cgpa):
    """
    Validate CGPA between 0 and 4.0
    """
    try:
        cgpa_float = float(cgpa)
        return 0 <= cgpa_float <= 4.0
    except ValueError:
        return False

def create_labeled_entry(parent, label_text, variable):
    """
    Create a labeled entry with a specific variable.
    """
    label = tk.Label(parent, text=label_text, font=("Arial", 12))
    label.pack(pady=10)

    entry = tk.Entry(
        parent, 
        textvariable=variable, 
        width=50, 
        font=("Arial", 12)
    )
    entry.pack(pady=5)
    return entry

def add_student_form(root):
    """
    Create the form to add a student.
    """
    frame = tk.Frame(root)
    frame.pack(pady=20)

    # Create variables for new fields
    name_var = tk.StringVar()
    roll_no_var = tk.StringVar()
    section_var = tk.StringVar()
    credit_hours_attempted_var = tk.IntVar()
    credit_hours_earned_var = tk.IntVar()
    cgpa_var = tk.DoubleVar()
    warning_status_var = tk.IntVar(value=0)
    enrollment_status_var = tk.StringVar()
    specialization_var = tk.StringVar()

    # Create labeled entry fields
    create_labeled_entry(frame, "Student Name", name_var)
    create_labeled_entry(frame, "Roll Number", roll_no_var)
    create_labeled_entry(frame, "Section", section_var)
    create_labeled_entry(frame, "Credit Hours Attempted", credit_hours_attempted_var)
    create_labeled_entry(frame, "Credit Hours Earned", credit_hours_earned_var)
    create_labeled_entry(frame, "CGPA", cgpa_var)

    # Warning Status as Spinbox (0-3)
    warning_label = tk.Label(frame, text="Warning Status", font=("Arial", 12))
    warning_label.pack(pady=10)
    warning_spinbox = tk.Spinbox(
        frame, 
        from_=0, 
        to=3, 
        textvariable=warning_status_var, 
        width=50, 
        font=("Arial", 12)
    )
    warning_spinbox.pack(pady=5)

    # Enrollment Status Dropdown
    enrollment_status_label = tk.Label(frame, text="Enrollment Status", font=("Arial", 12))
    enrollment_status_label.pack(pady=10)
    enrollment_status_dropdown = ttk.Combobox(
        frame, 
        textvariable=enrollment_status_var, 
        values=["Current", "Suspended", "Finished"], 
        width=47, 
        font=("Arial", 12),
        state="readonly"
    )
    enrollment_status_dropdown.pack(pady=5)

    create_labeled_entry(frame, "Specialization", specialization_var)

    # Add Submit button
    def submit():
        # Retrieve values
        name = name_var.get().strip()
        roll_no = roll_no_var.get().strip()
        section = section_var.get().strip()
        credit_hours_attempted = credit_hours_attempted_var.get()
        credit_hours_earned = credit_hours_earned_var.get()
        cgpa = cgpa_var.get()
        warning_status = warning_status_var.get()
        enrollment_status = enrollment_status_var.get().strip()
        specialization = specialization_var.get().strip()

        # Validation checks
        errors = []

        # 1. Name validation (not empty)
        if not name:
            errors.append("Student Name cannot be empty")

        # 2. Roll Number validation (xxp-xxxx format)
        if not validate_roll_no(roll_no):
            errors.append("Invalid Roll Number. Format must be xxp-xxxx (e.g., 22p-1234)")
        
        # 2.1 Check if Roll Number already exists in database
        if roll_no_exists(roll_no):
            errors.append("Roll Number already exists in the database")

        # 3. Section validation (not empty)
        if not section:
            errors.append("Section cannot be empty")

        # 4. Credit Hours Attempted validation (> 0)
        if credit_hours_attempted <= 0:
            errors.append("Credit Hours Attempted must be greater than 0")

        # 5. Credit Hours Earned validation (≤ Attempted)
        if credit_hours_earned < 0 or credit_hours_earned > credit_hours_attempted:
            errors.append("Credit Hours Earned must be between 0 and Credit Hours Attempted")

        # 6. CGPA validation (0-4.0)
        if not validate_cgpa(cgpa):
            errors.append("CGPA must be between 0 and 4.0")

        # 7. Warning Status validation (0-3)
        if warning_status < 0 or warning_status > 3:
            errors.append("Warning Status must be between 0 and 3")

        # 8. Enrollment Status validation (not empty)
        if not enrollment_status:
            errors.append("Enrollment Status must be selected")

        # 9. Specialization validation (not empty)
        if not specialization:
            errors.append("Specialization cannot be empty")

        # Check if there are any validation errors
        if errors:
            # Show all validation errors
            messagebox.showerror("Validation Errors", "\n".join(errors))
            return
        
        # Insert student record
        if database.insert_student(
            roll_no, name, section, 
            credit_hours_attempted, credit_hours_earned, 
            cgpa, warning_status, 
            enrollment_status, specialization
        ):
            messagebox.showinfo("Success", f"Student {name} added successfully!")
            
            # Clear form after successful submission
            name_var.set("")
            roll_no_var.set("")
            section_var.set("")
            credit_hours_attempted_var.set(0)
            credit_hours_earned_var.set(0)
            cgpa_var.set(0.0)
            warning_status_var.set(0)
            enrollment_status_var.set("")
            specialization_var.set("")

    submit_btn = tk.Button(frame, text="Add Student", command=submit, font=("Arial", 12))
    submit_btn.pack(pady=10)

    return frame