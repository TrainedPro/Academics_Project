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

