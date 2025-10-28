from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
from typing import Optional, Union

# Import our modules
from database import (
    init_db, get_all_contacts, get_contact_by_id, create_contact, 
    update_contact, delete_contact, log_contact, check_duplicate_name
)
from models import ContactCreate, ContactUpdate, ContactLog
from ai_service import draft_message
from email_service import send_email, check_daily_reminders

app = FastAPI(title="StayInTouch API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
init_db()

@app.get("/")
async def root():
    return {"message": "StayInTouch API is running!", "current_time": datetime.now().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/contacts")
async def get_contacts():
    """Get all contacts"""
    contacts = get_all_contacts()
    return {"contacts": contacts}

@app.post("/contacts")
async def add_contact(contact: ContactCreate):
    """Add a new contact"""
    # Check for duplicate names (case-insensitive)
    if check_duplicate_name(contact.name):
        return {"error": "A contact with this name already exists"}
    
    contact_id = create_contact(contact)
    return {"message": "Contact added successfully", "contact_id": contact_id}

@app.get("/contacts/{contact_id}")
async def get_contact(contact_id: int):
    """Get a specific contact"""
    contact = get_contact_by_id(contact_id)
    if not contact:
        return {"error": "Contact not found"}
    return contact

@app.put("/contacts/{contact_id}")
async def update_contact_endpoint(contact_id: int, contact: ContactUpdate):
    """Update a contact"""
    # Check if contact exists
    existing_contact = get_contact_by_id(contact_id)
    if not existing_contact:
        return {"error": "Contact not found"}
    
    # Check for duplicate names if name is being updated
    if contact.name and contact.name != existing_contact['name']:
        if check_duplicate_name(contact.name, exclude_id=contact_id):
            return {"error": "A contact with this name already exists"}
    
    update_contact(contact_id, contact)
    return {"message": "Contact updated successfully"}

@app.delete("/contacts/{contact_id}")
async def delete_contact_endpoint(contact_id: int):
    """Delete a contact"""
    contact = get_contact_by_id(contact_id)
    if not contact:
        return {"error": "Contact not found"}
    
    delete_contact(contact_id)
    return {"message": "Contact deleted successfully"}

@app.get("/reminders")
async def get_reminders():
    """Get contacts that need attention"""
    contacts = get_all_contacts()
    reminders = []
    today = datetime.now()
    
    for contact in contacts:
        contact_id = contact['id']
        name = contact['name']
        whatsapp = contact['whatsapp_number']
        birthday = contact['birthday']
        frequency = contact['reminder_frequency_days']
        last_contact = contact['last_contact_date']
        notes = contact['notes']
        contact_group = contact['contact_group']
        
        # Check for birthday reminders for ALL contacts (if they have a birthday)
        birthday_reminder_added = False
        if birthday:
            try:
                # Parse birthday and calculate days until next birthday
                birthday_date = datetime.strptime(birthday, '%Y-%m-%d')
                this_year_birthday = birthday_date.replace(year=today.year)
                
                # Calculate days until birthday using date only (ignore time)
                today_date = today.date()
                birthday_date_only = this_year_birthday.date()
                days_until_birthday = (birthday_date_only - today_date).days

                if last_contact:
                    days_since = int((today - datetime.strptime(last_contact, '%Y-%m-%d')).days)
                else:
                    days_since = None
                
                # Show reminder on birthday or shortly after
                if days_until_birthday <= 0 and days_until_birthday >= -3:
                    reminders.append({
                        "id": contact_id,
                        "name": name,
                        "whatsapp_number": whatsapp,
                        "birthday": birthday,
                        "reminder_frequency_days": frequency,
                        "last_contact_date": last_contact,
                        "notes": notes,
                        "days_since_contact": days_since,
                        "status": "birthday_reminder",
                        "debug": {
                            "server_date": today.isoformat(),
                            "birthday": birthday,
                            "days_until_birthday": days_until_birthday
                        }
                    })
                    birthday_reminder_added = True
            except ValueError:
                # Invalid birthday format, skip birthday check
                pass
        
        # Check for regular frequency-based reminders (only if not birthday-only)
        if frequency != 'Birthday only' and not birthday_reminder_added:
            if last_contact:
                days_since = int((today - datetime.strptime(last_contact, '%Y-%m-%d')).days)
            else:
                # If never contacted, treat as overdue immediately
                days_since = 999  # Large number to ensure it shows as overdue
            
            if isinstance(frequency, str): # Handle case where frequency is 'Birthday only'
                continue # Skip if it's a birthday only contact and no birthday reminder was added
            
            if days_since >= frequency:
                reminders.append({
                    "id": contact_id,
                    "name": name,
                    "whatsapp_number": whatsapp,
                    "birthday": birthday,
                    "reminder_frequency_days": frequency,
                    "last_contact_date": last_contact,
                    "notes": notes,
                    "days_since_contact": days_since,
                    "status": "overdue" if days_since >= frequency else "due_soon"
                })
    
    return {"reminders": reminders}

@app.post("/contacts/{contact_id}/log")
async def log_contact_endpoint(contact_id: int, log_data: ContactLog):
    """Log a contact interaction"""
    contact = get_contact_by_id(contact_id)
    if not contact:
        return {"error": "Contact not found"}
    
    log_contact(contact_id, log_data.contact_date, log_data.method, log_data.notes)
    return {"message": "Contact logged successfully"}

@app.post("/test-email")
async def test_email():
    """Test email sending"""
    success = send_email("Test Email", "This is a test email from StayInTouch!")
    return {"success": success, "message": "Test email sent" if success else "Failed to send test email"}

@app.post("/send-reminders-now")
async def send_reminders_now():
    """Manually trigger reminder check"""
    check_daily_reminders()
    return {"message": "Reminder check completed"}

@app.post("/draft-message/{contact_id}")
async def draft_message_endpoint(contact_id: int, custom_prompt: str = ""):
    """Draft a personalized message for a contact"""
    try:
        # Get contact information
        contact = get_contact_by_id(contact_id)
        
        if not contact:
            return {"error": "Contact not found"}
        
        # Draft the message
        message = draft_message(contact, custom_prompt)
        
        return {
            "success": True,
            "message": message,
            "contact_name": contact['name']
        }
        
    except Exception as e:
        return {"error": f"Failed to draft message: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)