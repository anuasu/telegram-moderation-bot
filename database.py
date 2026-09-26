import sqlite3

DATABASE_NAME = "bot_database.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            warnings INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moderation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            admin_id INTEGER,
            action TEXT,
            reason TEXT,
            duration TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, username, first_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (user_id, username, first_name, warnings)
        VALUES (?, ?, ?, 0)
    """, (user_id, username, first_name))

    cursor.execute("""
        UPDATE users
        SET username = ?, first_name = ?
        WHERE user_id = ?
    """, (username, first_name, user_id))

    conn.commit()
    conn.close()


def get_warnings(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT warnings FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result[0] if result else 0


def add_warning(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET warnings = warnings + 1
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

    return get_warnings(user_id)


def remove_warning(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET warnings = CASE
            WHEN warnings > 0 THEN warnings - 1
            ELSE 0
        END
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

    return get_warnings(user_id)


def reset_warnings(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET warnings = 0
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def add_log(user_id, admin_id, action, reason="", duration=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO moderation_logs
        (user_id, admin_id, action, reason, duration)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, admin_id, action, reason, duration))

    conn.commit()
    conn.close()