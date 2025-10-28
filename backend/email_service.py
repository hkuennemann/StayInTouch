import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from datetime import datetime
from database import get_all_contacts

# Load environment variables
load_dotenv()

# Email configuration
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 587))
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_TO = os.getenv('EMAIL_TO')

def send_email(subject, body):
    """Send email notification"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, EMAIL_TO, text)
        server.quit()
        
        print(f"Email sent successfully: {subject}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def check_daily_reminders():
    """Check for reminders and send email if any exist"""
    try:
        # Get all contacts
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
            
            # Check for birthday reminders first
            birthday_reminder_added = False
            if birthday:
                try:
                    birthday_date = datetime.strptime(birthday, '%Y-%m-%d')
                    this_year_birthday = birthday_date.replace(year=today.year)
                    today_date = today.date()
                    birthday_date_only = this_year_birthday.date()
                    days_until_birthday = (birthday_date_only - today_date).days
                    
                    if days_until_birthday <= 0 and days_until_birthday >= -3:
                        reminders.append(f"🎂 {name} - Birthday reminder")
                        birthday_reminder_added = True
                except ValueError:
                    pass
            
            # Check for regular frequency reminders (only if no birthday reminder was added)
            if not birthday_reminder_added and frequency != 'Birthday only':
                days_since = 0
                if last_contact:
                    days_since = int((today - datetime.strptime(last_contact, '%Y-%m-%d')).days)
                
                if days_since >= frequency:
                    reminders.append(f"📞 {name} - Overdue by {days_since - frequency} days")
        
        # Send email if there are reminders
        if reminders:
            subject = f"StayInTouch Reminders - {len(reminders)} contacts need attention"
            body = f"Hello!\n\nYou have {len(reminders)} contacts that need your attention:\n\n"
            body += "\n".join(reminders)
            body += f"\n\nVisit your StayInTouch app to contact them!\n\nBest regards,\nStayInTouch"
            
            send_email(subject, body)
        else:
            print("No reminders today - no email sent")
            
    except Exception as e:
        print(f"Error checking reminders: {e}")
