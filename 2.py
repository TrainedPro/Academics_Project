import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect('university.db')

# Query to retrieve students meeting the specified criteria
query = '''
SELECT DISTINCT
    Students.Roll_No,
    Students.Name,
    Students.Status,
    Grades_DS.Grade AS Data_Structures_Grade,
    Grades_OOP.Grade AS Object_Oriented_Programming_Grade
FROM Students
LEFT JOIN Grades AS Grades_DS ON Students.Roll_No = Grades_DS.Roll_No AND Grades_DS.Course_Code = 'CS2001'
JOIN Grades AS Grades_OOP ON Students.Roll_No = Grades_OOP.Roll_No AND Grades_OOP.Course_Code = 'CS1004'
WHERE Students.Status = 'current'
  AND (Grades_DS.Grade IS NULL OR Grades_DS.Grade = '')
  AND Grades_OOP.Grade NOT IN ('F', 'W', 'I');
'''

# Execute query and load results into a DataFrame
result = pd.read_sql_query(query, conn)

# Display the results
print(result)

# Close the connection
conn.close()
