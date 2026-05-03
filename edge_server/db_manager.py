import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'majidawa.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Table 1: Threads (Conversations)
    c.execute('''CREATE TABLE IF NOT EXISTS threads 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  phone_number TEXT, 
                  status TEXT DEFAULT 'active', 
                  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                  
    # Table 2: Messages (Individual SMS linked to a thread)
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  thread_id INTEGER, 
                  role TEXT, 
                  content TEXT, 
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(thread_id) REFERENCES threads(id))''')
                  
    # Table 3: Verified Users (Security Layer + Preferences)
    c.execute('''CREATE TABLE IF NOT EXISTS verified_users 
                 (phone_number TEXT PRIMARY KEY, 
                  user_type TEXT DEFAULT 'patient', 
                  preferred_lang TEXT DEFAULT 'kirundi',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
                  
    conn.commit()
    conn.close()

def get_user_lang(phone_number):
    """Retrieves the preferred language for a verified user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT preferred_lang FROM verified_users WHERE phone_number=?", (phone_number,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 'kirundi'

def set_user_lang(phone_number, lang):
    """Updates the preferred language for a verified user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE verified_users SET preferred_lang=? WHERE phone_number=?", (lang.lower(), phone_number))
    conn.commit()
    conn.close()

def is_verified(phone_number):
    """Checks if a phone number is registered in the system."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT 1 FROM verified_users WHERE phone_number=?", (phone_number,))
    result = c.fetchone()
    conn.close()
    return result is not None

def register_user(phone_number, user_type='patient'):
    """Registers a new user (usually via an admin command or first-time setup)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO verified_users (phone_number, user_type) VALUES (?, ?)", (phone_number, user_type))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Already exists
    conn.close()

def get_active_thread(phone_number):
    """Finds the currently active thread for a user, or creates one if none exists."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check for an active thread
    c.execute("SELECT id, last_updated FROM threads WHERE phone_number=? AND status='active' ORDER BY last_updated DESC LIMIT 1", (phone_number,))
    row = c.fetchone()
    
    if row:
        thread_id = row[0]
        last_updated_str = row[1]
        
        # TIMEOUT LOGIC: If the last message was more than 24 hours ago, auto-close it and start a new one.
        # (This handles users who forget to text "NEW")
        last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d %H:%M:%S')
        if datetime.now() - last_updated > timedelta(hours=24):
            close_thread(thread_id)
            return create_new_thread(phone_number, conn)
            
        return thread_id
    else:
        return create_new_thread(phone_number, conn)

def create_new_thread(phone_number, conn=None):
    """Closes old threads and starts a fresh one."""
    close_connection = False
    if conn is None:
        conn = sqlite3.connect(DB_NAME)
        close_connection = True
        
    c = conn.cursor()
    # Close any existing active threads for this number
    c.execute("UPDATE threads SET status='closed' WHERE phone_number=? AND status='active'", (phone_number,))
    
    # Create new thread
    c.execute("INSERT INTO threads (phone_number, status, last_updated) VALUES (?, 'active', CURRENT_TIMESTAMP)", (phone_number,))
    new_thread_id = c.lastrowid
    
    conn.commit()
    if close_connection:
        conn.close()
        
    return new_thread_id

def close_thread(thread_id):
    """Forces a thread to close."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE threads SET status='closed' WHERE id=?", (thread_id,))
    conn.commit()
    conn.close()

def add_message(thread_id, role, content):
    """Saves a message to the database and updates the thread's timestamp."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Insert message
    c.execute("INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)", (thread_id, role, content))
    
    # Update thread timestamp
    c.execute("UPDATE threads SET last_updated=CURRENT_TIMESTAMP WHERE id=?", (thread_id,))
    
    conn.commit()
    conn.close()

def get_thread_history(thread_id):
    """Retrieves the history of a specific thread formatted for Gemma."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Fetch last 10 messages to avoid token overload
    c.execute("SELECT role, content FROM messages WHERE thread_id=? ORDER BY id ASC LIMIT 10", (thread_id,))
    messages = c.fetchall()
    conn.close()
    
    history = ""
    for msg in messages:
        role = "Patient" if msg[0] == 'user' else "Nurse"
        history += f"{role}: {msg[1]}\n"
        
    return history