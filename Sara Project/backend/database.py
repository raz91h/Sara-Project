import sqlite3
from datetime import datetime

DATABASE = "sara.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        jabatan TEXT,
        nip TEXT UNIQUE,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ANNOUNCEMENTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        judul TEXT NOT NULL,
        isi TEXT NOT NULL,
        tipe TEXT DEFAULT 'info',
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(created_by) REFERENCES users(id)
    )
    """)

    # SUBMISSIONS (Cuti/Izin/Sakit)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nama TEXT NOT NULL,
        nip TEXT NOT NULL,
        jenis TEXT NOT NULL,
        tanggal_mulai DATE NOT NULL,
        tanggal_selesai DATE NOT NULL,
        alasan TEXT,
        lampiran TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # RATINGS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        nama TEXT,
        rating INTEGER NOT NULL,
        saran TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # CHAT LOGS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_message TEXT,
        bot_response TEXT,
        source TEXT DEFAULT 'kb',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # DEFAULT ADMIN
    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO users (nama, username, password, email, nip, role)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ("Administrator HRD", "admin", "admin123", "hr@samaratu.com", "HR001", "admin"))

    conn.commit()
    conn.close()

def create_user(nama, username, password, email="", jabatan="", nip=""):
    conn = get_db_connection()
    try:
        conn.execute("""
        INSERT INTO users (nama, username, password, email, jabatan, nip)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (nama, username, password, email, jabatan, nip))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        raise Exception("Username atau NIP sudah terdaftar!")

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def update_user_password(user_id, new_password):
    """Update user password"""
    conn = get_db_connection()
    try:
        conn.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        raise Exception(f"Gagal mengubah password: {str(e)}")

def create_announcement(judul, isi, tipe, admin_id):
    conn = get_db_connection()
    conn.execute("""
    INSERT INTO announcements (judul, isi, tipe, created_by)
    VALUES (?, ?, ?, ?)
    """, (judul, isi, tipe, admin_id))
    conn.commit()
    conn.close()

def get_announcements():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM announcements ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in data]

def create_submission(user_id, nama, nip, jenis, tanggal_mulai, tanggal_selesai, alasan, lampiran=None):
    conn = get_db_connection()
    conn.execute("""
    INSERT INTO submissions (user_id, nama, nip, jenis, tanggal_mulai, tanggal_selesai, alasan, lampiran)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, nama, nip, jenis, tanggal_mulai, tanggal_selesai, alasan, lampiran))
    conn.commit()
    conn.close()

def get_submissions(user_id=None):
    conn = get_db_connection()
    if user_id:
        data = conn.execute("SELECT * FROM submissions WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    else:
        data = conn.execute("SELECT * FROM submissions ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in data]

def update_submission_status(submission_id, status):
    conn = get_db_connection()
    conn.execute("UPDATE submissions SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (status, submission_id))
    conn.commit()
    conn.close()

def create_rating(user_id, nama, rating, saran):
    conn = get_db_connection()
    conn.execute("INSERT INTO ratings (user_id, nama, rating, saran) VALUES (?, ?, ?, ?)", (user_id, nama, rating, saran))
    conn.commit()
    conn.close()

def get_ratings():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM ratings ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in data]

def save_chat(user_id, user_message, bot_response, source='kb'):
    conn = get_db_connection()
    conn.execute("INSERT INTO chat_logs (user_id, user_message, bot_response, source) VALUES (?, ?, ?, ?)", 
                 (user_id, user_message, bot_response, source))
    conn.commit()
    conn.close()

def get_chat_logs(limit=100):
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM chat_logs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in data]

def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chat_logs WHERE date(created_at) = date('now')")
    chat_today = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM chat_logs")
    chat_total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM submissions")
    total_cuti = cursor.fetchone()[0]
    cursor.execute("SELECT AVG(rating) FROM ratings")
    avg_rating = cursor.fetchone()[0] or 0
    pengumuman = get_announcements()[:5]
    conn.close()
    return {
        "chat_today": chat_today,
        "chat_total": chat_total,
        "total_cuti": total_cuti,
        "avg_rating": round(avg_rating, 1),
        "pengumuman": pengumuman
    }
