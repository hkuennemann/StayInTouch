# StayInTouch

A personal contact reminder system to help you stay connected with friends and family.

## Features

- 📱 **Contact Management**: Add, edit, and organize your contacts
- 🎂 **Birthday Reminders**: Never miss a birthday again
- 📧 **Email Notifications**: Daily reminders sent to your email
- 🤖 **AI Message Drafting**: Generate personalized WhatsApp messages using Gemini AI
- 📊 **Contact Groups**: Organize contacts by family, friends, work, etc.
- ⏰ **Custom Reminder Frequencies**: Set how often you want to be reminded

## Quick Start

### Prerequisites

- Python 3.10+
- Gmail account (for email notifications)
- Gemini API key (for AI message drafting)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd StayInTouch
```

2. Set up the backend:
```bash
cd backend
python -m venv StayInTouch_venv
source StayInTouch_venv/bin/activate  # On Windows: StayInTouch_venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp env.template backend/.env
# Edit backend/.env with your actual values
```

4. Start the server:
```bash
python app.py
```

5. Open the frontend:
```bash
# Open frontend/index.html in your browser
```

## Configuration

### Email Setup

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Update `backend/.env` with your email credentials

### AI Setup

1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add it to `backend/.env` as `GEMINI_API_KEY`

### Automatic Reminders

The system can be set up to send daily email reminders automatically using macOS LaunchAgent:

```bash
# Copy the plist file to LaunchAgents directory
cp config/com.stayintouch.reminders.plist ~/Library/LaunchAgents/

# Load the service
launchctl load ~/Library/LaunchAgents/com.stayintouch.reminders.plist
```

## Project Structure

```
StayInTouch/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── database.py         # Database operations
│   ├── models.py           # Pydantic models
│   ├── ai_service.py       # AI functionality
│   ├── email_service.py    # Email operations
│   ├── prompts.py          # AI prompts
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── style.css           # Styling
│   └── script.js           # Frontend logic
├── config/
│   ├── start_server.sh     # Server startup script
│   ├── check_reminders.sh  # Reminder check script
│   └── com.stayintouch.reminders.plist  # macOS LaunchAgent
└── env.template            # Environment variables template
```

## Usage

1. **Add Contacts**: Use the web interface to add friends and family
2. **Set Reminders**: Choose how often you want to be reminded (weekly, monthly, etc.)
3. **Get Notifications**: Receive daily email reminders for contacts that need attention
4. **Draft Messages**: Use AI to generate personalized WhatsApp messages
5. **Track Interactions**: Log when you contact someone to update reminder schedules

## API Endpoints

- `GET /contacts` - Get all contacts
- `POST /contacts` - Add a new contact
- `PUT /contacts/{id}` - Update a contact
- `DELETE /contacts/{id}` - Delete a contact
- `GET /reminders` - Get contacts needing attention
- `POST /draft-message/{id}` - Generate AI message for contact
- `POST /contacts/{id}/log` - Log a contact interaction

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
