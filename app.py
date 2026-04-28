import os
import sqlite3
import requests
import g4f
from datetime import date
from flask import Flask, render_template, request, jsonify
from g4f.client import Client

# Fix for Render template detection
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# Initialize Database if missing (Required for hosting)
def init_db():
    db_path = os.path.join(base_dir, 'database.db')
    if not os.path.exists(db_path):
        print("Database not found. Initializing...")
        from create_db import conn as db_conn
        db_conn.close()
        print("Database initialized.")

init_db()

# Set local directory for g4f to avoid sandbox permission errors
os.environ['G4F_DIR'] = os.path.join(os.getcwd(), '.g4f_cache')
if not os.path.exists(os.environ['G4F_DIR']):
    os.makedirs(os.environ['G4F_DIR'])

# Free AI Client (No API Key required)
client = Client()

@app.route('/ask-ai', methods=['POST'])
def ask_ai():
    try:
        data = request.json
        messages = data.get("messages", [])
        
        # If single message is provided instead of messages list
        if not messages and "message" in data:
            messages = [{"role": "user", "content": data["message"]}]

        # Try to get a response from g4f using specific free providers
        try:
            from g4f.Provider import PollinationsAI, BlackboxPro, ItalyGPT
            
            # Attempt 1: PollinationsAI (very reliable)
            try:
                response = client.chat.completions.create(
                    model="openai",
                    messages=messages,
                    provider=PollinationsAI
                )
                reply = response.choices[0].message.content
            except Exception as e1:
                print(f"PollinationsAI failed: {e1}")
                # Attempt 2: General gpt-3.5-turbo with excluded bad providers
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    ignore_providers=["PuterJS", "OpenRouter", "OpenAI", "Groq", "Anthropic", "Google"]
                )
                reply = response.choices[0].message.content

        except Exception as ai_err:
            print(f"Primary AI Error: {ai_err}")
            # Final Fallback: try any working provider without restrictions
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                reply = response.choices[0].message.content
            except Exception as e_final:
                print(f"Final AI Error: {e_final}")
                reply = "I'm currently having trouble connecting to my brain, but I'm still here to help! Please try again in a moment."


        return jsonify({
            "choices": [
                {
                    "message": {
                        "content": reply
                    }
                }
            ]
        })
    except Exception as e:
        print(f"Final AI Error: {e}")
        # Last resort fallback: a friendly mock response that uses the data
        return jsonify({
            "choices": [
                {
                    "message": {
                        "content": "I'm currently having trouble connecting to my brain, but I'm still here to help! Please try again in a moment. (Technical error: " + str(e) + ")"
                    }
                }
            ]
        })

# =========================
# ROUTES → PAGES
# =========================

# Login Page
@app.route('/')
def home():
    return render_template('login.html')


# =========================
# LOGIN API
# =========================
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        print("LOGIN ATTEMPT:", email, password, role)  # Debug

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        
        if user:
            user_role = user[0]
            teacher_data = None
            student_data = None

            if user_role == 'teacher':
                cursor.execute("SELECT name, subject, classes FROM teachers WHERE email=?", (email,))
                teacher = cursor.fetchone()
                if teacher:
                    teacher_data = {
                        "name": teacher[0],
                        "subject": teacher[1],
                        "classes": teacher[2].split(',')
                    }
            
            elif user_role == 'student':
                # Fetch detailed student data including marks
                cursor.execute("""
                    SELECT s.id, s.name, s.class, s.roll_no, s.attendance, s.performance, s.fee_status, s.pending_amount,
                           m.telugu, m.hindi, m.english, m.maths, m.science, m.social
                    FROM students s
                    LEFT JOIN marks m ON s.id = m.student_id
                    WHERE s.email = ?
                """, (email,))
                s = cursor.fetchone()
                if s:
                    student_data = {
                        "id": s[0],
                        "name": s[1],
                        "class": s[2],
                        "roll_no": s[3],
                        "attendance": s[4],
                        "performance": s[5],
                        "fee_status": s[6],
                        "pending": s[7],
                        "marks": {
                            "telugu": s[8] if s[8] is not None else 0,
                            "hindi": s[9] if s[9] is not None else 0,
                            "english": s[10] if s[10] is not None else 0,
                            "maths": s[11] if s[11] is not None else 0,
                            "science": s[12] if s[12] is not None else 0,
                            "social": s[13] if s[13] is not None else 0
                        }
                    }
            
            conn.close()
            return jsonify({
                "status": "success",
                "role": user_role,
                "teacher": teacher_data,
                "student": student_data
            })

        conn.close()
        return jsonify({
            "status": "error",
            "message": "Invalid email or password"
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "status": "error",
            "message": "Server error"
        })


# =========================
# DASHBOARD ROUTES
# =========================

@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/teacher')
def teacher():
    return render_template('teacher.html')


@app.route('/student')
def student():
    return render_template('student.html')


# =========================
# ADMIN FEATURE ROUTES
# =========================

@app.route('/admin/students')
def admin_students():
    return render_template('admin_students.html')


@app.route('/admin/teachers')
def admin_teachers():
    return render_template('admin_teachers.html')


@app.route('/classes')
def classes():
    return render_template('classes.html')


@app.route('/fees')
def fees():
    return render_template('feemanagement.html')


@app.route('/attendance')
def attendance():
    return render_template('attendance.html')


@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


@app.route('/ai')
def ai():
    return render_template('ai-assistant.html')
# =========================
# STUDENT APIs
# =========================


# Add Student
@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data.get('name')
    student_class = data.get('class')
    roll_no = data.get('roll_no')
    attendance = data.get('attendance', '0%')
    performance = data.get('performance', 'N/A')
    fee_status = data.get('fee_status', 'Pending')
    pending = data.get('pending', '₹0')

    if not name or not student_class:
        return jsonify({
            "status": "error",
            "message": "All fields required"
        })

    # Auto-generate roll number if not provided
    if not roll_no or roll_no == '-' or roll_no == '':
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT roll_no FROM students WHERE class = ? ORDER BY id DESC LIMIT 1", (student_class,))
        last_roll = cursor.fetchone()
        if last_roll and last_roll[0] and last_roll[0].isdigit():
            roll_no = str(int(last_roll[0]) + 1)
        else:
            # Default for class (e.g., 101 for 1A, 201 for 2A)
            try:
                class_num = ''.join(filter(str.isdigit, student_class))
                roll_no = f"{class_num}01" if class_num else "101"
            except:
                roll_no = "101"
        conn.close()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students (name, class, roll_no, attendance, performance, fee_status, pending_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, student_class, roll_no, attendance, performance, fee_status, pending))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

@app.route('/teacher/add_students', methods=['POST'])
def teacher_add_students():
    data = request.get_json()
    students_list = data.get('students', [])

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    for s in students_list:
        name = s.get('name')
        student_class = s.get('class')
        marks = s.get('marks')

        if not name:
            continue

        # Generate Roll Number: Last Roll No in class + 1
        cursor.execute("SELECT roll_no FROM students WHERE class = ? ORDER BY id DESC LIMIT 1", (student_class,))
        last_roll = cursor.fetchone()
        new_roll = "101" # Default if class is empty
        if last_roll and last_roll[0] and last_roll[0].isdigit():
            new_roll = str(int(last_roll[0]) + 1)
        elif last_roll and last_roll[0]:
            # If it's something like '301', try to increment it
            import re
            match = re.search(r'(\d+)$', last_roll[0])
            if match:
                new_roll = last_roll[0][:match.start()] + str(int(match.group(1)) + 1)

        # Insert student
        cursor.execute("""
            INSERT INTO students (name, class, roll_no, attendance, performance, fee_status, pending_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, student_class, new_roll, "0%", "N/A", "Pending", "0"))
        
        student_id = cursor.lastrowid

        # Insert marks
        cursor.execute("""
            INSERT INTO marks (student_id, telugu, hindi, english, maths, science, social)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (student_id, marks['telugu'], marks['hindi'], marks['english'], marks['maths'], marks['science'], marks['social']))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})


# Get All Teachers
@app.route('/get_all_teachers')
def get_all_teachers():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, email, subject, classes FROM teachers")
    teachers = cursor.fetchall()

    conn.close()

    result = []
    for t in teachers:
        result.append({
            "name": t[0],
            "email": t[1],
            "subject": t[2],
            "classes": t[3].split(',') if t[3] else []
        })

    return jsonify(result)

@app.route('/get_attendance_stats')
def get_attendance_stats():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Get attendance for the last 7 days
    cursor.execute("""
        SELECT date, 
               SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
               SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent
        FROM attendance_records
        GROUP BY date
        ORDER BY date DESC
        LIMIT 7
    """)
    rows = cursor.fetchall()
    conn.close()
    
    # Format data for chart
    result = []
    for r in reversed(rows):
        d_obj = date.fromisoformat(r[0])
        result.append({
            "date": r[0],
            "day": d_obj.strftime("%a"),
            "present": r[1],
            "absent": r[2]
        })
    
    return jsonify(result)

@app.route('/get_analytics_data')
def get_analytics_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 1. Subject Radar Data (Overall Average)
    cursor.execute("SELECT AVG(telugu), AVG(hindi), AVG(english), AVG(maths), AVG(science), AVG(social) FROM marks")
    avg_marks = cursor.fetchone()
    radar_data = [round(m, 1) if m else 0 for m in avg_marks]
    
    # 2. Class-wise Fee Stats
    cursor.execute("""
        SELECT class, 
               SUM(CASE WHEN fee_status = 'Paid' THEN 1 ELSE 0 END) as paid_count,
               COUNT(*) as total_count,
               SUM(CAST(REPLACE(REPLACE(pending_amount, '₹', ''), ',', '') AS FLOAT)) as total_pending
        FROM students
        GROUP BY class
    """)
    fee_rows = cursor.fetchall()
    
    # 3. AI Insights Logic
    cursor.execute("SELECT COUNT(*) FROM students WHERE performance = 'At Risk'")
    at_risk_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT name FROM students WHERE performance = 'Excellent' LIMIT 5")
    top_students = [r[0] for r in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        "radar": radar_data,
        "fee_stats": [{
            "class": r[0],
            "paid": r[1],
            "total": r[2],
            "pending": r[3]
        } for r in fee_rows],
        "insights": {
            "at_risk": at_risk_count,
            "top_students": top_students
        }
    })

@app.route('/get_student_weekly_attendance/<int:student_id>')
def get_student_weekly_attendance(student_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Get last 7 days of attendance for this specific student
    cursor.execute("""
        SELECT date, status
        FROM attendance_records
        WHERE student_id = ?
        ORDER BY date DESC
        LIMIT 7
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in reversed(rows):
        d_obj = date.fromisoformat(r[0])
        result.append({
            "date": r[0],
            "day": d_obj.strftime("%a"),
            "status": r[1]
        })
    
    return jsonify(result)

@app.route('/get_class_weekly_stats/<teacher_class>')
def get_class_weekly_stats(teacher_class):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Get attendance for the last 7 days for this specific class
    cursor.execute("""
        SELECT ar.date, 
               SUM(CASE WHEN ar.status = 'Present' THEN 1 ELSE 0 END) as present,
               SUM(CASE WHEN ar.status = 'Absent' THEN 1 ELSE 0 END) as absent
        FROM attendance_records ar
        JOIN students s ON ar.student_id = s.id
        WHERE s.class = ?
        GROUP BY ar.date
        ORDER BY ar.date DESC
        LIMIT 7
    """, (teacher_class,))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in reversed(rows):
        d_obj = date.fromisoformat(r[0])
        result.append({
            "date": r[0],
            "day": d_obj.strftime("%a"),
            "present": r[1],
            "absent": r[2]
        })
    
    return jsonify(result)

@app.route('/get_full_school_data')
def get_full_school_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Fetch all students with their marks
    cursor.execute("""
        SELECT s.id, s.name, s.class, s.roll_no, s.attendance, s.performance, s.fee_status, s.pending_amount,
               m.telugu, m.hindi, m.english, m.maths, m.science, m.social
        FROM students s
        LEFT JOIN marks m ON s.id = m.student_id
    """)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        result.append({
            "name": r[1],
            "class": r[2],
            "roll_no": r[3],
            "attendance": r[4],
            "performance": r[5],
            "fee_status": r[6],
            "pending": r[7],
            "marks": {
                "telugu": r[8] if r[8] is not None else 0,
                "hindi": r[9] if r[9] is not None else 0,
                "english": r[10] if r[10] is not None else 0,
                "maths": r[11] if r[11] is not None else 0,
                "science": r[12] if r[12] is not None else 0,
                "social": r[13] if r[13] is not None else 0
            }
        })
    
    return jsonify(result)

@app.route('/delete_student', methods=['POST'])
def delete_student():
    data = request.get_json()
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({"status": "error", "message": "No student ID provided"})

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # Delete related records first
        cursor.execute("DELETE FROM marks WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM attendance_records WHERE student_id = ?", (student_id,))
        
        # Finally delete student
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        conn.close()
        return jsonify({"status": "error", "message": str(e)})

# Get All Students
@app.route('/get_all_students')
def get_all_students():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    result = []
    for s in students:
        result.append({
            "id": s[0],
            "name": s[1],
            "class": s[2],
            "roll_no": s[3],
            "attendance": s[4],
            "performance": s[5],
            "fee_status": s[6],
            "pending": s[7],
            "email": s[8] if len(s) > 8 else None
        })

    return jsonify(result)

@app.route('/record_payment', methods=['POST'])
def record_payment():
    data = request.get_json()
    student_id = data.get('student_id')
    amount_paid = float(data.get('amount_paid'))
    payment_mode = data.get('payment_mode')
    today = date.today().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 1. Add to payments table
    cursor.execute("INSERT INTO payments (student_id, amount, mode, date) VALUES (?, ?, ?, ?)", (student_id, amount_paid, payment_mode, today))

    # 2. Update current pending amount in students table
    cursor.execute("SELECT pending_amount, fee_status FROM students WHERE id = ?", (student_id,))
    res = cursor.fetchone()
    if res:
        current_pending = float(res[0].replace('₹', '').replace(',', '')) if isinstance(res[0], str) else float(res[0])
        new_pending = max(0, current_pending - amount_paid)
        new_status = 'Paid' if new_pending == 0 else 'Partial'
        
        cursor.execute("UPDATE students SET pending_amount = ?, fee_status = ? WHERE id = ?", (f"₹{new_pending:,.0f}", new_status, student_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "new_pending": new_pending, "new_status": new_status})
    
    conn.close()
    return jsonify({"status": "error", "message": "Student not found"})

@app.route('/get_admin_dashboard_stats')
def get_admin_dashboard_stats():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Total Students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    # Total Teachers
    cursor.execute("SELECT COUNT(*) FROM teachers")
    total_teachers = cursor.fetchone()[0]

    # Pending Fees
    cursor.execute("SELECT SUM(CAST(REPLACE(REPLACE(pending_amount, '₹', ''), ',', '') AS FLOAT)) FROM students")
    total_pending = cursor.fetchone()[0] or 0

    # Total Collected (Estimate based on payments table)
    cursor.execute("SELECT SUM(amount) FROM payments")
    total_collected = cursor.fetchone()[0] or 0

    # Active Classes
    cursor.execute("SELECT COUNT(DISTINCT class) FROM students")
    active_classes = cursor.fetchone()[0]

    # Attendance Today
    today = date.today().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE date = ?", (today,))
    total_att = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE date = ? AND status = 'Present'", (today,))
    present_att = cursor.fetchone()[0]
    attendance_today = (present_att / total_att * 100) if total_att > 0 else 97.2 # Default fallback

    # Recent Payments
    cursor.execute("""
        SELECT s.name, s.class, p.amount, p.mode, p.date 
        FROM payments p 
        JOIN students s ON p.student_id = s.id 
        ORDER BY p.id DESC LIMIT 5
    """)
    recent_payments = [{ "name": r[0], "class": r[1], "amount": r[2], "mode": r[3], "date": r[4] } for r in cursor.fetchall()]

    # Students with Pending Fees
    cursor.execute("""
        SELECT name, class, pending_amount, fee_status 
        FROM students 
        WHERE fee_status != 'Paid' 
        ORDER BY CAST(REPLACE(REPLACE(pending_amount, '₹', ''), ',', '') AS FLOAT) DESC 
        LIMIT 5
    """)
    pending_students = [{ "name": r[0], "class": r[1], "pending": r[2], "status": r[3] } for r in cursor.fetchall()]

    # Performance Breakdown
    cursor.execute("SELECT performance, COUNT(*) FROM students GROUP BY performance")
    perf_rows = cursor.fetchall()
    perf_data = { "High": 0, "Average": 0, "At Risk": 0 }
    total_perf = 0
    for r in perf_rows:
        p_name = "High" if "High" in r[0] or "Excellent" in r[0] or "Good" in r[0] else ("At Risk" if "Risk" in r[0] else "Average")
        perf_data[p_name] += r[1]
        total_perf += r[1]
    
    perf_stats = { k: round(v/total_perf*100) if total_perf > 0 else 0 for k, v in perf_data.items() }

    conn.close()

    return jsonify({
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_pending": f"₹{(total_pending/1000):.0f}K" if total_pending > 1000 else f"₹{total_pending}",
        "total_collected": f"₹{(total_collected/100000):.1f}L" if total_collected > 100000 else f"₹{total_collected}",
        "active_classes": active_classes,
        "attendance_today": f"{attendance_today:.1f}%",
        "recent_payments": recent_payments,
        "pending_students": pending_students,
        "performance_stats": perf_stats
    })

# Get All Students by Class
@app.route('/get_students_by_class/<teacher_class>')
def get_students_by_class(teacher_class):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    today = date.today().strftime("%Y-%m-%d")

    # Join students with marks and today's attendance
    cursor.execute("""
        SELECT s.id, s.name, s.class, s.roll_no, s.attendance, s.performance, s.fee_status, s.pending_amount,
               m.telugu, m.hindi, m.english, m.maths, m.science, m.social,
               ar.status as today_status
        FROM students s
        LEFT JOIN marks m ON s.id = m.student_id
        LEFT JOIN attendance_records ar ON s.id = ar.student_id AND ar.date = ?
        WHERE s.class=?
    """, (today, teacher_class,))
    students = cursor.fetchall()

    conn.close()

    result = []
    for s in students:
        result.append({
            "id": s[0],
            "name": s[1],
            "class": s[2],
            "roll_no": s[3],
            "attendance": s[4],
            "performance": s[5],
            "fee_status": s[6],
            "pending": s[7],
            "marks": {
                "telugu": s[8] if s[8] is not None else 0,
                "hindi": s[9] if s[9] is not None else 0,
                "english": s[10] if s[10] is not None else 0,
                "maths": s[11] if s[11] is not None else 0,
                "science": s[12] if s[12] is not None else 0,
                "social": s[13] if s[13] is not None else 0
            },
            "today_attendance": s[14] if s[14] is not None else 'N/A'
        })

    return jsonify(result)

@app.route('/save_attendance', methods=['POST'])
def save_attendance():
    data = request.get_json()
    attendance_list = data.get('attendance', [])
    today = date.today().strftime("%Y-%m-%d")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    for item in attendance_list:
        student_id = item.get('student_id')
        status = item.get('status')

        # Check if attendance already marked for today
        cursor.execute("SELECT id FROM attendance_records WHERE student_id = ? AND date = ?", (student_id, today))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("UPDATE attendance_records SET status = ? WHERE id = ?", (status, existing[0]))
        else:
            cursor.execute("INSERT INTO attendance_records (student_id, date, status) VALUES (?, ?, ?)", (student_id, today, status))

        # Update student's overall attendance percentage
        cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE student_id = ?", (student_id,))
        total_days = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE student_id = ? AND status = 'Present'", (student_id,))
        present_days = cursor.fetchone()[0]
        
        if total_days > 0:
            percentage = round((present_days / total_days) * 100)
            cursor.execute("UPDATE students SET attendance = ? WHERE id = ?", (f"{percentage}%", student_id))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

@app.route('/save_marks', methods=['POST'])
def save_marks():
    data = request.get_json()
    marks_list = data.get('marks', [])

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    for item in marks_list:
        student_id = item.get('student_id')
        m = item.get('marks')

        # Check if marks already exist for this student
        cursor.execute("SELECT id FROM marks WHERE student_id = ?", (student_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE marks
                SET telugu = ?, hindi = ?, english = ?, maths = ?, science = ?, social = ?
                WHERE student_id = ?
            """, (m['telugu'], m['hindi'], m['english'], m['maths'], m['science'], m['social'], student_id))
        else:
            cursor.execute("""
                INSERT INTO marks (student_id, telugu, hindi, english, maths, science, social)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_id, m['telugu'], m['hindi'], m['english'], m['maths'], m['science'], m['social']))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

@app.route('/update_student', methods=['POST'])
def update_student():
    data = request.get_json()

    student_id = data.get('id')
    attendance = data.get('attendance')
    performance = data.get('performance')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students
        SET attendance = ?, performance = ?
        WHERE id = ?
    """, (attendance, performance, student_id))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)