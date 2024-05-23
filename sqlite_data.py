import sqlite3
import uuid

# Membuat koneksi ke database SQLite
conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Membuat tabel untuk Face Recognition
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS face_data (
    face_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    face_encoding TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS face_recognition_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    recognized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
''')

# Creating tables for Face Recognition, Fatigue Analysis, etc.
cursor.execute('''
CREATE TABLE employees (
    employee_id TEXT PRIMARY KEY,
    name TEXT,
    position TEXT,
    department TEXT,
    photo BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS shift_schedules (
    shift_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    shift_start DATETIME,
    shift_end DATETIME,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS workloads (
    workload_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    work_date DATE,
    tasks_assigned INTEGER,
    tasks_completed INTEGER,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS sleep_logs (
    sleep_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    sleep_date DATE,
    sleep_duration FLOAT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS fatigue_analysis_logs (
    analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    analysis_date DATE,
    fatigue_level TEXT,
    comments TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
)
''')

# Menyimpan perubahan dan menutup koneksi
conn.commit()
conn.close()

# Function to insert a new employee record into the database
def insert_employee(name, department, position, photo, created_at):
    conn = sqlite3.connect('company.db')
    c = conn.cursor()
    
    # Generate UUID for id
    employee_id = str(uuid.uuid4())
    
    # Read the photo data
    # with open(photo_path, 'rb') as f:
    #     photo_data = f.read()
    
    # Insert employee data into the table
    c.execute("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)",
              (employee_id, name, department, position, photo, created_at))
    
    # Commit changes
    conn.commit()
    
    # Close connection
    conn.close()

# Example usage
insert_employee("Dimas", "Artificial Intelligence", "AI", "ID/Dimas - HK.jpg", "2024-05-22")
