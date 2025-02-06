import sqlite3

def create_connection():
    return sqlite3.connect('database.db')

def create_users_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_user(username, password, email):
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (username, password, email) VALUES (?, ?, ?)
    ''', (username, password, email))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    user = c.fetchone()
    conn.close()
    return user

def reset_password(username, new_password):
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE users SET password = ? WHERE username = ?
    ''', (new_password, username))
    conn.commit()
    conn.close()

def check_user_exists(username):
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        SELECT * FROM users WHERE username = ?
    ''', (username,))
    user = c.fetchone()
    conn.close()
    return user is not None

def create_comments_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            comment TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            origin_city TEXT NOT NULL,
            origin_area TEXT NOT NULL,
            destination_city TEXT NOT NULL,
            destination_area TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_comment(name, comment, sentiment, origin_city, origin_area, destination_city, destination_area):
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO comments (name, comment, sentiment, origin_city, origin_area, destination_city, destination_area) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, comment, sentiment, origin_city, origin_area, destination_city, destination_area))
    conn.commit()
    conn.close()

def get_all_comments():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''
        SELECT * FROM comments ORDER BY timestamp DESC
    ''')
    comments = c.fetchall()
    conn.close()
    return comments

def clear_database():
    conn = create_connection()
    c = conn.cursor()
    # Delete all records from users and comments tables
    c.execute('DELETE FROM users')
    c.execute('DELETE FROM comments')
    conn.commit()
    conn.close()
