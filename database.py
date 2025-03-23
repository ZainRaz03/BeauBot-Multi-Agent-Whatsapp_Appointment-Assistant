import sqlite3
import os
from datetime import datetime

DB_FILE = "spa_booking.db"

def init_db():
    """Initialize the database with required tables"""
    db_exists = os.path.exists(DB_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        email TEXT,
        is_member INTEGER DEFAULT 1,
        is_deleted INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        user_message TEXT,
        bot_reply TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES chats (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        duration INTEGER NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS artists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        experience INTEGER NOT NULL,
        expertise TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        booking_time TIMESTAMP NOT NULL,
        product_id INTEGER NOT NULL,
        status TEXT DEFAULT 'booked',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (artist_id) REFERENCES artists (id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')
    
    if not db_exists:
        cursor.execute('''
        INSERT INTO users (name, phone, email, is_member) VALUES 
        ('Zain Raza', '+923065187343', 'zainxaidi2003@gmail.com', 1),
        ('John Doe', '+12345678901', 'john@example.com', 1),
        ('Jane Smith', '+12345678902', 'jane@example.com', 0)
        ''')
        

        cursor.execute('''
        INSERT INTO products (name, price, duration) VALUES 
        ('Haircut', 30.00, 30),
        ('Manicure', 25.00, 45),
        ('Facial', 50.00, 60),
        ('Hair Coloring', 75.00, 90),
        ('Massage', 60.00, 60)
        ''')
        
        cursor.execute('''
        INSERT INTO artists (name, experience, expertise) VALUES 
        ('John', 5, 'Hair Styling'),
        ('Sarah', 7, 'Nail Care'),
        ('Emma', 10, 'Skin Care'),
        ('Michael', 8, 'Hair Coloring'),
        ('Lisa', 12, 'Massage Therapy')
        ''')
    
    conn.commit()
    conn.close()

def execute_query(query, params=None, fetch=True):
    """Execute an SQL query and return results if needed"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            if query.strip().upper().startswith("SELECT"):
               
                results = [dict(row) for row in cursor.fetchall()]
                conn.close()
                return results
            else:
                conn.commit()
                last_id = cursor.lastrowid
                conn.close()
                return {"id": last_id}
        else:
            conn.commit()
            conn.close()
            return {"success": True}
    except Exception as e:
        conn.close()
        raise e 