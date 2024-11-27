import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui_components
import utils

# Predefined Options
PROGRAM_OPTIONS = [
    "Computer Science", 
    "Software Engineering", 
    "Artificial Intelligence", 
    "Data Science"
]

SEMESTER_OPTIONS = ["1", "2", "3", "4", "5", "6", "7", "8"]

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Fast Batch Advisor Automation")
    root.geometry("900x650")

    # Create a frame for the left sidebar
    sidebar_frame = tk.Frame(root, width=220, bg="#2C3E50")
    sidebar_frame.pack(side="left", fill="y")

    # Create a main content frame
    content_frame = tk.Frame(root)
    content_frame.pack(side="right", fill="both", expand=True)

    # Create a Notebook widget for the tab structure
    notebook = ttk.Notebook(content_frame)
    notebook.pack(fill="both", expand=True)

    # Sidebar Button Style
    button_style = {
        'font': ("Arial", 12),
        'width': 22,
        'bd': 0,
        'fg': 'white',
        'activeforeground': 'white'
    }

    # Fetch course options from database
    conn = database.connect_database('project.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT course_title FROM courses")
    COURSE_OPTIONS = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Create UI Pages
    courses_page = ui_components.create_courses_page(notebook, PROGRAM_OPTIONS, SEMESTER_OPTIONS)
    eligible_page = ui_components.create_eligible_students_page(notebook, COURSE_OPTIONS)
    add_course_page = ui_components.create_add_course_page(notebook)
    manage_grades_page = ui_components.create_manage_grades_page(notebook) 
    # Create Teachers Page
    teachers_page = ui_components.create_teachers_page(notebook)
    add_student_page = ui_components.add_student_form(notebook)  # Add the Add Student page


    

    # New Manage Grades Page
    

    # Add pages to the notebook
    notebook.add(courses_page, text="Show Courses")
    notebook.add(eligible_page, text="Show Eligible Students")
    notebook.add(add_course_page, text="Add Course")
    notebook.add(manage_grades_page, text="Manage Grades")  # Add Manage Grades Tab
    notebook.add(teachers_page, text="Manage Teachers")
    notebook.add(add_student_page, text="Add Student")
    # Create sidebar buttons
    ui_components.create_sidebar_buttons(sidebar_frame, notebook, button_style)

    # Add a sidebar button for Manage Grades
    manage_grades_button = tk.Button(
        sidebar_frame, 
        text="Manage Grades", 
        command=lambda: notebook.select(notebook.tabs()[-2]),  # Navigate to Manage Grades Tab
        bg="#9B59B6", 
        activebackground="#8E44AD", 
        font=("Arial", 12), 
        width=22, 
        bd=0, 
        fg='white', 
        activeforeground='white'
    )
    manage_grades_button.pack(pady=10)
    
    
    manage_teacher_button = tk.Button(
        sidebar_frame, 
        text="Manage Teachers", 
        command=lambda: notebook.select(notebook.tabs()[-1]),  # Navigate to Manage Grades Tab
        bg="#9B59B6", 
        activebackground="#8E44AD", 
        font=("Arial", 12), 
        width=22, 
        bd=0, 
        fg='white', 
        activeforeground='white'
    )
    manage_teacher_button.pack(pady=10)

    # Run the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()
