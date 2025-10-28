#!/usr/bin/env python3
"""
Standalone StayInTouch utility script
This can be run independently of the FastAPI server

Usage:
    python send_reminders.py [init|reminders|test-email]
    
    init         - Initialize database only
    reminders    - Send email reminders (default)
    test-email   - Send a test email
"""

import sys
import os
from database import init_db
from email_service import check_daily_reminders, send_email

def init_database():
    """Initialize database only"""
    print("StayInTouch Database Initialization")
    print("=" * 40)
    print("Initializing database...")
    init_db()
    print("✓ Database initialized successfully!")

def send_reminders():
    """Initialize database and send reminders"""
    print("StayInTouch Email Reminder System")
    print("=" * 40)
    
    # Initialize database if needed
    print("Initializing database...")
    init_db()
    print("✓ Database ready")
    
    # Check and send reminders
    print("Checking for reminders...")
    check_daily_reminders()
    print("✓ Reminder check completed")

def test_email():
    """Send a test email"""
    print("StayInTouch Test Email")
    print("=" * 40)
    
    # Initialize database if needed
    print("Initializing database...")
    init_db()
    print("✓ Database ready")
    
    # Send test email
    print("Sending test email...")
    result = send_email(
        "Test Email from StayInTouch", 
        "This is a test email to verify the email system is working correctly!"
    )
    
    if result:
        print("✓ Test email sent successfully!")
    else:
        print("✗ Failed to send test email")

def main():
    """Main function with command line argument support"""
    command = sys.argv[1] if len(sys.argv) > 1 else "reminders"
    
    if command == "init":
        init_database()
    elif command == "reminders":
        send_reminders()
    elif command == "test-email":
        test_email()
    else:
        print("Usage: python send_reminders.py [init|reminders|test-email]")
        print("  init         - Initialize database only")
        print("  reminders    - Send email reminders (default)")
        print("  test-email   - Send a test email")
        sys.exit(1)

if __name__ == "__main__":
    main()
