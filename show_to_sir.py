import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import csv

# Function to get courses based on program and semester
def fetch_courses_by_program_and_semester(program, semester, cursor):
    query = '''
    SELECT c.course_title
    FROM program_courses pc
    JOIN courses c ON pc.course_code = c.course_code
    WHERE pc.program_name = ? AND pc.semester = ?;
    '''
    cursor.execute(query, (program, semester))
    courses = cursor.fetchall()
    return [course[0] for course in courses]

# Function to get prerequisite course code for a given course name
def get_prerequisite(course_name, cursor):
    query = '''
    SELECT prerequisite_course_code
    FROM courses
    WHERE course_title = ?;
    '''
    cursor.execute(query, (course_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

# Function to get eligible students for the given course name
def get_eligible_students(db_path, course_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    prerequisite_course_code = get_prerequisite(course_name, cursor)
    
    if prerequisite_course_code:
        query = '''
        SELECT 
            s.name
        FROM 
            students s
        JOIN 
            grades g
        ON 
            s.roll_no = g.roll_no
        JOIN 
            courses c
        ON 
            g.course_code = c.course_code
        WHERE 
            c.course_title = ? 
            AND g.grade  IN ('-', 'F', 'W', 'I')
            AND EXISTS (
                SELECT 1
                FROM courses prerequisite
                WHERE prerequisite.course_code = c.prerequisite_course_code
                AND prerequisite.course_code = ?
            );
        '''
        cursor.execute(query, (course_name, prerequisite_course_code))
        students = cursor.fetchall()
        conn.close()

        return [student[0] for student in students], len(students)

    conn.close()
    return [], 0

# Function to handle the button click event for showing eligible students
def show_eligible_students(course_name_entry, result_label):
    course_name = course_name_entry.get()
    
    if not course_name:
        messagebox.showerror("Input Error", "Please enter a course name.")
        return

    eligible_students, count = get_eligible_students('project.sqlite3', course_name)

    if count == 0:
        messagebox.showinfo("No Eligible Students", f"No students are eligible for the course '{course_name}'.")
    else:
        result_text = f"Eligible Students Count: {count}\n\n" + "\n".join(eligible_students)
        
        sections = (count // 50) + (1 if count % 50 > 0 else 0)
        result_text += f"\n\nTotal Sections: {sections}"

        result_label.config(text=result_text)

# Function to handle the button click event for fetching courses
def show_courses(program_name_entry, semester_entry, courses_label):
    program = program_name_entry.get()
    semester = semester_entry.get()

    if not program or not semester:
        messagebox.showerror("Input Error", "Please enter both program and semester.")
        return

    conn = sqlite3.connect('project.sqlite3')
    cursor = conn.cursor()

    courses = fetch_courses_by_program_and_semester(program, semester, cursor)

    if not courses:
        messagebox.showinfo("No Courses", f"No courses found for {program} in Semester {semester}.")
    else:
        courses_text = "\n".join(courses)
        courses_label.config(text="Courses Offered:\n" + courses_text)

    conn.close()

# Function to export eligible students to CSV
def export_eligible_students_to_csv(eligible_students):
    if eligible_students:
        with open("eligible_students.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Student Name"])
            for student in eligible_students:
                writer.writerow([student])
        messagebox.showinfo("Success", "Eligible students exported to 'eligible_students.csv'.")
    else:
        messagebox.showinfo("No Data", "No eligible students to export.")

# Function to export courses to CSV
def export_courses_to_csv(courses):
    if courses:
        with open("courses.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Course Title"])
            for course in courses:
                writer.writerow([course])
        messagebox.showinfo("Success", "Courses exported to 'courses.csv'.")
    else:
        messagebox.showinfo("No Data", "No courses to export.")

# Create the main window
root = tk.Tk()
root.title("Fast Batch Advisor Automation")
root.geometry("600x600")

# Create a Notebook widget for the tab structure
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Main Menu Page
main_menu_page = ttk.Frame(notebook)
main_menu_page.pack(fill="both", expand=True)
notebook.add(main_menu_page, text="Main Menu")

# Add a background image to the main menu page
image = Image.open("/home/ac/Desktop/Academics_Project/pictures/f.png")  # Update with the correct file path
background_image = ImageTk.PhotoImage(image)
background_label = tk.Label(main_menu_page, image=background_image)
background_label.place(relwidth=1, relheight=1)

# Add a heading to the main menu page
heading_label = tk.Label(main_menu_page, text="Fast Batch Advisor Automation", font=("Arial", 16, "bold"), bg="#FF5733", fg="white", width=30)
heading_label.pack(pady=20)

# Add buttons for options
button_frame = ttk.Frame(main_menu_page)
button_frame.pack(pady=30)

show_courses_button = tk.Button(button_frame, text="Show Courses", command=lambda: notebook.select(courses_page), font=("Arial", 14), width=20, bg="#4CAF50", fg="white")
show_courses_button.grid(row=0, column=0, padx=10, pady=10)

show_eligible_button = tk.Button(button_frame, text="Show Eligible Students", command=lambda: notebook.select(eligible_page), font=("Arial", 14), width=20, bg="#FF9800", fg="white")
show_eligible_button.grid(row=1, column=0, padx=10, pady=10)

# Show Courses Page
courses_page = ttk.Frame(notebook)
courses_page.pack(fill="both", expand=True)
notebook.add(courses_page, text="Show Courses")

# Add widgets for courses page
program_name_label = tk.Label(courses_page, text="Enter Program Name:", font=("Arial", 12))
program_name_label.pack(pady=10)

program_name_entry = tk.Entry(courses_page, width=50, font=("Arial", 12))
program_name_entry.pack(pady=5)

semester_label = tk.Label(courses_page, text="Enter Semester Number:", font=("Arial", 12))
semester_label.pack(pady=10)

semester_entry = tk.Entry(courses_page, width=50, font=("Arial", 12))
semester_entry.pack(pady=5)

check_courses_button = tk.Button(courses_page, text="Check Courses", command=lambda: show_courses(program_name_entry, semester_entry, courses_label), font=("Arial", 12), bg="#4CAF50", fg="white")
check_courses_button.pack(pady=15)

courses_label = tk.Label(courses_page, text="Courses will appear here.", font=("Arial", 12))
courses_label.pack(pady=10)

export_courses_button = tk.Button(courses_page, text="Export Courses to CSV", command=lambda: export_courses_to_csv(courses_label.cget("text").split("\n")[1:]), font=("Arial", 12), bg="#FFC107", fg="white")
export_courses_button.pack(pady=10)

# Show Eligible Students Page
eligible_page = ttk.Frame(notebook)
eligible_page.pack(fill="both", expand=True)
notebook.add(eligible_page, text="Show Eligible Students")

# Add widgets for eligible students page
course_name_label = tk.Label(eligible_page, text="Enter Course Name to Check Eligibility:", font=("Arial", 12))
course_name_label.pack(pady=10)

course_name_entry = tk.Entry(eligible_page, width=50, font=("Arial", 12))
course_name_entry.pack(pady=5)

check_button = tk.Button(eligible_page, text="Check Eligibility", command=lambda: show_eligible_students(course_name_entry, result_label), font=("Arial", 12), bg="#FF9800", fg="white")
check_button.pack(pady=15)

result_label = tk.Label(eligible_page, text="Eligible students will appear here.", font=("Arial", 12))
result_label.pack(pady=10)

export_button = tk.Button(eligible_page, text="Export Eligible Students to CSV", command=lambda: export_eligible_students_to_csv(result_label.cget("text").split("\n")[1:]), font=("Arial", 12), bg="#FF9800", fg="white")
export_button.pack(pady=10)

# Run the application
root.mainloop()
