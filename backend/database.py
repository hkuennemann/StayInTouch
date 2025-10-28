import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE = "contacts.db"

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            whatsapp_number TEXT,
            birthday TEXT,
            reminder_frequency_days INTEGER DEFAULT 7,
            last_contact_date TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            contact_group TEXT DEFAULT 'friends'
        )
    ''')
    
    # Add contact_group column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE contacts ADD COLUMN contact_group TEXT DEFAULT "friends"')
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    # Create contact_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            contact_date TEXT NOT NULL,
            method TEXT DEFAULT 'whatsapp',
            notes TEXT,
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_all_contacts():
    """Get all contacts from database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts')
    rows = cursor.fetchall()
    conn.close()
    
    contacts = []
    for row in rows:
        contact_id, name, whatsapp, birthday, frequency, last_contact, notes, created_at, contact_group = row
        contacts.append({
            "id": contact_id,
            "name": name,
            "whatsapp_number": whatsapp,
            "birthday": birthday,
            "reminder_frequency_days": frequency,
            "last_contact_date": last_contact,
            "notes": notes,
            "created_at": created_at,
            "contact_group": contact_group
        })
    
    return contacts

def get_contact_by_id(contact_id):
    """Get a specific contact by ID"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    contact_id, name, whatsapp, birthday, frequency, last_contact, notes, created_at, contact_group = row
    return {
        "id": contact_id,
        "name": name,
        "whatsapp_number": whatsapp,
        "birthday": birthday,
        "reminder_frequency_days": frequency,
        "last_contact_date": last_contact,
        "notes": notes,
        "created_at": created_at,
        "contact_group": contact_group
    }

def create_contact(contact_data):
    """Create a new contact"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO contacts (name, whatsapp_number, birthday, reminder_frequency_days, last_contact_date, notes, contact_group)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        contact_data.name,
        contact_data.whatsapp_number,
        contact_data.birthday,
        contact_data.reminder_frequency_days,
        contact_data.last_contact_date,
        contact_data.notes,
        contact_data.contact_group
    ))
    
    contact_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return contact_id

def update_contact(contact_id, contact_data):
    """Update an existing contact"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE contacts 
        SET name = ?, whatsapp_number = ?, birthday = ?, reminder_frequency_days = ?, 
            last_contact_date = ?, notes = ?, contact_group = ?
        WHERE id = ?
    ''', (
        contact_data.name,
        contact_data.whatsapp_number,
        contact_data.birthday,
        contact_data.reminder_frequency_days,
        contact_data.last_contact_date,
        contact_data.notes,
        contact_data.contact_group,
        contact_id
    ))
    
    conn.commit()
    conn.close()

def delete_contact(contact_id):
    """Delete a contact"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
    
    conn.commit()
    conn.close()

def log_contact(contact_id, contact_date, method='whatsapp', notes=None):
    """Log a contact interaction"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Insert into contact_logs
    cursor.execute('''
        INSERT INTO contact_logs (contact_id, contact_date, method, notes)
        VALUES (?, ?, ?, ?)
    ''', (contact_id, contact_date, method, notes))
    
    # Update last_contact_date in contacts table
    cursor.execute('''
        UPDATE contacts 
        SET last_contact_date = ?
        WHERE id = ?
    ''', (contact_date, contact_id))
    
    conn.commit()
    conn.close()

def check_duplicate_name(name, exclude_id=None):
    """Check if a contact name already exists (case-insensitive)"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    if exclude_id:
        cursor.execute('SELECT COUNT(*) FROM contacts WHERE LOWER(name) = LOWER(?) AND id != ?', (name, exclude_id))
    else:
        cursor.execute('SELECT COUNT(*) FROM contacts WHERE LOWER(name) = LOWER(?)', (name,))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0
