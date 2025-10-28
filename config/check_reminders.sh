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

# Run the email check function directly
python -c "
import sys
sys.path.append('.')
from app import check_daily_reminders
check_daily_reminders()
"
