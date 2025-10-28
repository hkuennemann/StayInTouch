#!/bin/bash

# StayInTouch Email Check Script
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get the project root (parent of config directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables
source "$PROJECT_ROOT/backend/.env"

# Change to backend directory
cd "$BACKEND_DIR"

# Activate virtual environment
source StayInTouch_venv/bin/activate

# Initialize database and run the email check function
python -c "
import sys
sys.path.append('.')
from database import init_db
from email_service import check_daily_reminders
init_db()  # Initialize database if it doesn't exist
check_daily_reminders()
"
