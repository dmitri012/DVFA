# For convenience sake we won't use SQLAlchemy, but instead use sqlite
import sqlite3
from datetime import datetime
import hashlib

def init():
    db = sqlite3.connect('data.db')
    
    # Create table to store comments in
    db.cursor().execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, comment TEXT, date TEXT)')
    
    # Create table to store users with roles
    db.cursor().execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, is_admin INTEGER)')
    
    # Add default admin user if not exists (for demo purposes)
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        admin_password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)', ('admin', admin_password_hash, 1))
        db.commit()

    return db

def add(comment):
    db = init()
    db.cursor().execute('INSERT INTO comments (comment, date) VALUES (?, ?)', (comment, datetime.utcnow().strftime('%B %d %Y - %H:%M')))

    db.commit()

def get(query=None):
    db = init()
    results = []
    
    for(comment, date) in db.cursor().execute('SELECT comment, date FROM comments').fetchall():
        if query is None or query in comment:
            results.append((comment, date))

    return results

def authenticate_user(username, password):
    """
    Authenticate user by username and password.
    Returns user dict with username and is_admin status if valid, None otherwise.
    """
    db = init()
    cursor = db.cursor()
    
    # Hash the provided password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Query user from database
    cursor.execute('SELECT username, is_admin FROM users WHERE username = ? AND password_hash = ?', 
                   (username, password_hash))
    result = cursor.fetchone()
    
    if result:
        return {
            'username': result[0],
            'is_admin': bool(result[1])
        }
    return None