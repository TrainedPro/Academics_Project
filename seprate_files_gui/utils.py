import tkinter as tk
from tkinter import messagebox, ttk
import csv
import database
import sqlite3

def create_labeled_entry(parent, label_text, variable):
    """Create a labeled entry with a specific variable."""
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

import sqlite3
from tkinter import messagebox

def fetch_courses_from_db():
    """Fetch all available courses from the database."""
    conn = sqlite3.connect('project.sqlite3')
    cursor = conn.cursor()

    # Query to fetch all courses
    query = "SELECT course_code, course_title FROM courses"
    cursor.execute(query)
    courses = cursor.fetchall()

    conn.close()

    return courses

def populate_course_dropdown(courses, course_var):
    """Populate the course dropdown with available courses."""
    course_titles = [f"{course[0]} - {course[1]}" for course in courses]
    course_var.set(course_titles[0])  # Set the default value
    return course_titles

def show_courses(program_var, semester_var, courses_tree):
    """Show courses based on selected program and semester in a table view."""
    # Clear existing items
    for item in courses_tree.get_children():
        courses_tree.delete(item)

    program = program_var.get()
    semester = semester_var.get()

    if not program or not semester:
        messagebox.showerror("Input Error", "Please select both program and semester.")
        return

    conn = sqlite3.connect('project.sqlite3')
    cursor = conn.cursor()

    query = '''
    SELECT c.course_code, c.course_title, c.credit_hours
    FROM program_courses pc
    JOIN courses c ON pc.course_code = c.course_code
    WHERE pc.program_name = ? AND pc.semester = ?;
    '''
    cursor.execute(query, (program, semester))
    courses = cursor.fetchall()

    if not courses:
        messagebox.showinfo("No Courses", f"No courses found for {program} in Semester {semester}.")
    else:
        for course in courses:
            courses_tree.insert("", "end", values=course)

    conn.close()

def add_course_to_program(course_var, program_var, semester_var, courses_tree):
    """Add the selected course to the program for the selected semester."""
    selected_course = course_var.get()
    program = program_var.get()
    semester = semester_var.get()

    if not selected_course or not program or not semester:
        messagebox.showerror("Input Error", "Please select both program, semester, and course.")
        return

    course_code = selected_course.split(" - ")[0]  # Extract course code

    conn = sqlite3.connect('project.sqlite3')
    cursor = conn.cursor()

    try:
        query = '''
        INSERT INTO program_courses (program_name, semester, course_code)
        VALUES (?, ?, ?);
        '''
        cursor.execute(query, (program, semester, course_code))
        conn.commit()
        messagebox.showinfo("Course Added", f"Course {course_code} has been added to {program} for Semester {semester}.")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while adding the course: {str(e)}")
    finally:
        conn.close()

    # Refresh the course list
    show_courses(program_var, semester_var, courses_tree)

def remove_course_from_program(program_var, semester_var, courses_tree):
    """Remove the selected course from the program for the selected semester."""
    selected_item = courses_tree.selection()

    if not selected_item:
        messagebox.showerror("Selection Error", "Please select a course to remove.")
        return

    course_code = courses_tree.item(selected_item, "values")[0]
    program = program_var.get()
    semester = semester_var.get()

    conn = sqlite3.connect('project.sqlite3')
    cursor = conn.cursor()

    try:
        query = '''
        DELETE FROM program_courses
        WHERE program_name = ? AND semester = ? AND course_code = ?;
        '''
        cursor.execute(query, (program, semester, course_code))
        conn.commit()
        messagebox.showinfo("Course Removed", f"Course {course_code} has been removed from {program} for Semester {semester}.")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while removing the course: {str(e)}")
    finally:
        conn.close()

    # Refresh the course list
    show_courses(program_var, semester_var, courses_tree)

        
        
def show_eligible_students(course_name_var, result_label):
    """Show eligible students for a selected course."""
    course_name = course_name_var.get()
    
    if not course_name:
        messagebox.showerror("Input Error", "Please select a course name.")
        return

    eligible_students, count = database.get_eligible_students('project.sqlite3', course_name)

    if count == 0:
        messagebox.showinfo("No Eligible Students", f"No students are eligible for the course '{course_name}'.")
    else:
        result_text = f"Eligible Students Count: {count}\n\n" + "\n".join(eligible_students)
        
        sections = (count // 50) + (1 if count % 50 > 0 else 0)
        result_text += f"\n\nTotal Sections: {sections}"

        result_label.config(text=result_text)
        export_eligible_students_to_csv(eligible_students)

def add_course(course_code_var, course_title_var, credit_hours_var, prerequisite_course_code_var):
    """Add a new course to the database."""
    course_code = course_code_var.get()
    course_title = course_title_var.get()
    credit_hours = credit_hours_var.get()
    prerequisite_course_code = prerequisite_course_code_var.get()

    if not course_code or not course_title or not credit_hours:
        messagebox.showerror("Input Error", "Please fill in all the required fields.")
        return
    
    database.insert_course(course_code, course_title, credit_hours, prerequisite_course_code)
    messagebox.showinfo("Success", f"Course '{course_title}' added successfully!")

def export_eligible_students_to_csv(eligible_students):
    """Export list of eligible students to a CSV file."""
    if eligible_students:
        with open("eligible_students.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Student Name"])
            for student in eligible_students:
                writer.writerow([student])
        messagebox.showinfo("Success", "Eligible students exported to 'eligible_students.csv'.")
    else:
        messagebox.showinfo("No Data", "No eligible students to export.")

def submit_grade(roll_no_var, course_var, grade_var):
    """Submit the grade for a student."""
    roll_no = roll_no_var.get()
    course_info = course_var.get()
    grade = grade_var.get()

    if not roll_no or not course_info or not grade:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    # Extract course code from course_info
    course_code = course_info.split(" - ")[0]

    result = database.insert_grade(roll_no, course_code, grade)
    
    if "added" in result.lower():
        messagebox.showinfo("Success", result)
    elif "already exists" in result.lower():
        messagebox.showwarning("Warning", result)
    else:
        messagebox.showerror("Error", result)

        
        
def create_labeled_dropdown(parent, label_text, dropdown):
    """Create a labeled dropdown menu."""
    label = tk.Label(parent, text=label_text, font=("Arial", 12))
    label.pack(pady=10)

    dropdown.pack(pady=5)
    
import sqlite3
from tkinter import messagebox
import database  # Assuming you have a database module to manage DB connections


def add_teacher(teacher_name_var, subject_var):
    """Add a new teacher to the database."""
    teacher_name = teacher_name_var.get()
    specialty = subject_var.get()  # specialty corresponds to course_code

    if not teacher_name or not specialty:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    try:
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
        subject_var.set('')
        
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")


def fetch_teachers(teacher_tree):
    """Fetch all teachers from the database and populate the treeview."""
    try:
        conn = database.connect_database('project.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT name, specialty FROM teachers")  # specialty is the course_code
        teachers = cursor.fetchall()
        for teacher in teachers:
            teacher_tree.insert("", "end", values=teacher)  # Insert teacher's name and specialty (course_code)
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while fetching teachers: {str(e)}")


def assign_course_to_teacher(teacher_var, course_var, credit_hours_var):
    """Assign the selected course and credit hours to the selected teacher."""
    teacher_name = teacher_var.get()
    course_info = course_var.get()
    credit_hours = credit_hours_var.get()

    if not teacher_name or not course_info or not credit_hours:
        messagebox.showerror("Input Error", "Please select both a teacher, a course, and enter credit hours.")
        return

    # Extract the course code from the course_info (e.g., "CS101 - Introduction to CS")
    course_code = course_info.split(" - ")[0]

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
        
        # Insert the teacher-course relationship into the teacher_courses table
        query = '''
        INSERT INTO teacher_courses (teacher_id, course_code, credit_hours)
        VALUES (?, ?, ?)
        '''
        cursor.execute(query, (teacher_id, course_code, credit_hours))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", f"Course '{course_code}' successfully assigned to teacher '{teacher_name}' with {credit_hours} credit hours.")
        
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")


def refresh_teacher_dropdown(teacher_dropdown):
    """Refresh the teacher dropdown list with updated data from the database."""
    try:
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
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while refreshing the teacher dropdown: {str(e)}")


def refresh_teacher_table(teacher_tree):
    """Refresh the teacher list table with updated data from the database."""
    try:
        # Clear existing entries in the treeview
        for row in teacher_tree.get_children():
            teacher_tree.delete(row)

        conn = database.connect_database('project.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT name, specialty FROM teachers")  # specialty is the course_code
        teachers = cursor.fetchall()
        conn.close()

        # Insert teachers into the treeview
        for teacher in teachers:
            teacher_tree.insert("", "end", values=teacher)  # Insert teacher's name and specialty (course_code)
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while refreshing the teacher table: {str(e)}")
