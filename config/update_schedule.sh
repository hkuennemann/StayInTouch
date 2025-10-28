#!/bin/bash

# Script to update LaunchAgent with time from .env file
# This script reads SERVER_START_TIME from backend/.env and updates the plist

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get the project root (parent of config directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables from backend/.env
if [ -f "$PROJECT_ROOT/backend/.env" ]; then
    source "$PROJECT_ROOT/backend/.env"
else
    echo "Error: backend/.env file not found"
    exit 1
fi

# Parse SERVER_START_TIME (format: HH:MM)
if [ -n "$SERVER_START_TIME" ]; then
    HOUR=$(echo "$SERVER_START_TIME" | cut -d: -f1)
    MINUTE=$(echo "$SERVER_START_TIME" | cut -d: -f2)
    
    # Remove leading zeros for integer values
    HOUR=$((10#$HOUR))
    MINUTE=$((10#$MINUTE))
    
    echo "Setting server start time to: $HOUR:$MINUTE"
else
    echo "SERVER_START_TIME not set in .env, using default 9:00"
    HOUR=9
    MINUTE=0
fi

# Update the plist file
PLIST_FILE="$SCRIPT_DIR/com.stayintouch.server.plist"

# Create a temporary plist with the correct time
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stayintouch.reminders</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>bash</string>
        <string>-c</string>
        <string>SCRIPT_DIR="\$(dirname "\$0")"; cd "\$SCRIPT_DIR" && ./check_reminders.sh</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>$HOUR</integer>
        <key>Minute</key>
        <integer>$MINUTE</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>/tmp/stayintouch_reminders.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/stayintouch_reminders_error.log</string>
    
    <key>WorkingDirectory</key>
    <string>/tmp</string>
</dict>
</plist>
EOF

echo "Updated plist file with start time: $HOUR:$MINUTE"
echo "To apply changes, run:"
echo "  launchctl unload ~/Library/LaunchAgents/com.stayintouch.reminders.plist"
echo "  cp $PLIST_FILE ~/Library/LaunchAgents/"
echo "  launchctl load ~/Library/LaunchAgents/com.stayintouch.reminders.plist"
