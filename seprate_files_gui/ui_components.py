import tkinter as tk
from tkinter import ttk, messagebox
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


def create_eligible_students_page(notebook, course_options):
    """Create the Show Eligible Students page."""
    eligible_page = ttk.Frame(notebook)
    scrollable_eligible = ScrollableFrame(eligible_page)
    scrollable_eligible.pack(fill="both", expand=True)

    # Course Name Dropdown
    course_name_label = tk.Label(scrollable_eligible.scrollable_frame, text="Select Course Name:", font=("Arial", 12))
    course_name_label.pack(pady=10)

    course_name_var = tk.StringVar()
    course_name_dropdown = ttk.Combobox(
        scrollable_eligible.scrollable_frame, 
        textvariable=course_name_var, 
        values=course_options, 
        width=50, 
        state="readonly"
    )
    course_name_dropdown.pack(pady=5)

    # Result Label
    result_label = tk.Label(scrollable_eligible.scrollable_frame, text="", font=("Arial", 12), justify="left")
    result_label.pack(pady=20)

    # Show Eligible Students Button
    show_eligible_button = tk.Button(
        scrollable_eligible.scrollable_frame, 
        text="Show Eligible Students", 
        command=lambda: utils.show_eligible_students(course_name_var, result_label), 
        font=("Arial", 12)
    )
    show_eligible_button.pack(pady=10)

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