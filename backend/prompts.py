# AI Prompts for StayInTouch

MESSAGE_DRAFTING_PROMPT = """
You are helping me draft a personalized WhatsApp message to reconnect with a friend. 

Contact Information:
- Name: {name}
- Birthday: {birthday}
- Notes: {notes}
- Last contacted: {last_contact_date}
- Contact group: {contact_group}

Please draft a warm, friendly, and personal message that:
1. Is appropriate for WhatsApp
2. Shows genuine care and interest
3. References their birthday if it's recent or upcoming
4. Mentions any relevant notes if appropriate
5. Is conversational and not too formal
6. Keeps it concise (2-3 sentences max)

{custom_prompt}

Draft the message now:
"""