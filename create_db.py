import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# =========================
# USERS TABLE (LOGIN)
# =========================
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT
)
''')

# Insert sample users safely
users = [
    ("admin@school.com", "1234", "admin"),
    ("teacher@school.com", "1234", "teacher"),
    ("student@school.com", "1234", "student")
]

for user in users:
    try:
        cursor.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", user)
    except:
        pass


# =========================
# STUDENTS TABLE
# =========================
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    class TEXT,
    roll_no TEXT,
    attendance TEXT,
    performance TEXT,
    fee_status TEXT,
    pending_amount TEXT         
)
''')


# =========================
# TEACHERS TABLE
# =========================
cursor.execute("DROP TABLE IF EXISTS teachers")
cursor.execute('''
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    name TEXT,
    subject TEXT,
    classes TEXT -- Store classes as comma-separated values like '1A,2A,10B'
)
''')

# =========================
# MARKS TABLE
# =========================
cursor.execute("DROP TABLE IF EXISTS marks")
cursor.execute('''
CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    telugu INTEGER DEFAULT 0,
    hindi INTEGER DEFAULT 0,
    english INTEGER DEFAULT 0,
    maths INTEGER DEFAULT 0,
    science INTEGER DEFAULT 0,
    social INTEGER DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students (id)
)
''')

# =========================
# ATTENDANCE TABLE
# =========================
cursor.execute("DROP TABLE IF EXISTS attendance_records")
cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    date TEXT,
    status TEXT, -- 'Present' or 'Absent'
    FOREIGN KEY (student_id) REFERENCES students (id)
)
''')

# =========================
# PAYMENTS TABLE
# =========================
cursor.execute("DROP TABLE IF EXISTS payments")
cursor.execute('''
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    amount REAL,
    mode TEXT, -- 'UPI', 'Cash', 'Bank Transfer'
    date TEXT,
    FOREIGN KEY (student_id) REFERENCES students (id)
)
''')

# Insert some sample payments
sample_payments = [
    (1, 5000, 'UPI', '2026-04-19'),
    (2, 10000, 'Bank Transfer', '2026-04-18'),
    (3, 15000, 'Cash', '2026-04-17')
]
for p in sample_payments:
    cursor.execute("INSERT INTO payments (student_id, amount, mode, date) VALUES (?, ?, ?, ?)", p)

conn.commit()

# Insert sample teachers safely
teachers_data = [
    ("teacher@school.com", "Dr. Sunita Rao", "Mathematics", "1A,2A,10A"),
    ("rajesh@school.com", "Mr. Rajesh Kumar", "Science", "3B,4A,9B"),
    ("anita@school.com", "Ms. Anita Sharma", "English", "5A,6B,7A,8B")
]

for t in teachers_data:
    try:
        cursor.execute("INSERT INTO teachers (email, name, subject, classes) VALUES (?, ?, ?, ?)", t)
    except:
        pass

# Insert students for some of these classes
students_data = [
    ("John Doe", "1A", "101", "95%", "Good", "Paid", "0"),
    ("Jane Smith", "1A", "102", "88%", "Average", "Pending", "500"),
    ("Bob Wilson", "1B", "103", "92%", "Excellent", "Paid", "0"),
    ("Alice Wonderland", "10A", "1001", "98%", "Excellent", "Paid", "0"),
    ("Charlie Brown", "10A", "1002", "75%", "Average", "Pending", "1200"),
    ("David Copperfield", "3B", "301", "85%", "Good", "Paid", "0")
]

for s in students_data:
    try:
        cursor.execute("INSERT INTO students (name, class, roll_no, attendance, performance, fee_status, pending_amount) VALUES (?, ?, ?, ?, ?, ?, ?)", s)
    except:
        pass

# Insert login for new teachers
teacher_users = [
    ("rajesh@school.com", "1234", "teacher"),
    ("anita@school.com", "1234", "teacher")
]
for u in teacher_users:
    try:
        cursor.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", u)
    except:
        pass

# Insert student logins for existing students
student_users = [
    ("john@school.com", "1234", "student"),
    ("jane@school.com", "1234", "student"),
    ("bob@school.com", "1234", "student"),
    ("alice@school.com", "1234", "student")
]
for u in student_users:
    try:
        cursor.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", u)
    except:
        pass

# Fetch all students and generate logins
cursor.execute("SELECT name FROM students")
all_students = cursor.fetchall()

for (name,) in all_students:
    email = name.lower().replace(' ', '.') + "@school.com"
    # Update student email
    cursor.execute("UPDATE students SET email = ? WHERE name = ?", (email, name))
    # Create user login
    try:
        cursor.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (email, "1234", "student"))
    except:
        pass

conn.commit()
conn.close()

print("Database setup complete!")