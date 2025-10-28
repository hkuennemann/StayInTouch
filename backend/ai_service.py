import os
import google.generativeai as genai
from dotenv import load_dotenv
from prompts import MESSAGE_DRAFTING_PROMPT

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def draft_message(contact_info, custom_prompt=""):
    """Draft a personalized message using Gemini AI"""
    try:
        # Format the prompt with contact info
        prompt = MESSAGE_DRAFTING_PROMPT.format(
            name=contact_info.get('name', 'Friend'),
            birthday=contact_info.get('birthday', 'Not specified'),
            notes=contact_info.get('notes', 'No notes'),
            last_contact_date=contact_info.get('last_contact_date', 'Unknown'),
            contact_group=contact_info.get('contact_group', 'friends'),
            custom_prompt=f"\nAdditional context: {custom_prompt}" if custom_prompt else ""
        )
        
        # Generate the message
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Failed to draft message: {e}")
        return "Sorry, I couldn't generate a message right now. Please try again later."
