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

    notebook.add(courses_page, text="Show Courses")
    notebook.add(eligible_page, text="Show Eligible Students")
    notebook.add(add_course_page, text="Add Course")

    # Create sidebar buttons
    ui_components.create_sidebar_buttons(sidebar_frame, notebook, button_style)

    # Run the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()