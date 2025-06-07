import os
import re
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
load_dotenv('.env', override=True)
import anthropic

logger = logging.getLogger(__name__)

CURRENT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
with open(CURRENT_DIR / 'templates' / 'prompt_body.txt', 'r') as file:
    PROMPT_BODY = file.read()
with open(CURRENT_DIR / 'templates' / 'prompt_notes.txt', 'r') as file:
    PROMPT_NOTES = file.read()

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
def _is_valid_email(s: str) -> bool:
    return s and re.match(EMAIL_REGEX, s) is not None


def get_emails() -> list[dict]:
    """
    Reads emails from the JSON file and returns them as a list of dictionaries.
    """
    with open('emails.json', 'r') as file:
        emails = json.load(file)
    logger.debug(f'Loaded {len(emails)} emails from JSON file.')
    
    # No need to return email body, this is just for indexing
    emails = [{ f: email.get(f) for f in ['id', 'from', 'patient_name', 'subject'] } for email in emails]
    return emails


def get_email_by_id(email_id: str) -> dict | None:
    """
    Retrieves a specific email by its ID.
    """
    if email_id is None or len(email_id) == 0:
        raise AttributeError('No email ID provided')
    
    logger.debug(f'Retrieving email with ID: {email_id}')
    with open('emails.json', 'r') as file:
        emails = json.load(file)
    
    for email in emails:
        if email.get('id') == email_id:
            logger.debug(f'Found email with ID: {email_id}')
            return email
    logger.warning(f'Email with ID: {email_id} not found.')
    return None
        

def create_email(email: dict) -> dict:
    """
    Creates a new email and appends it to the JSON file.

    Assumptions: this endpoint doesn't require "patient_name". I would
    assume there would be another service responsible for managing patient data.
    Also not including date/time as this would typically be handled by the database.
    """
    if not _is_valid_email(email.get("to", None)) \
       or len(email.get("body", "")) == 0:
        raise ValueError('Invalid email data')
    
    if email.get("subject", None) is None:
        email["subject"] = "No Subject"
    
    with open('sent.json', 'r+') as file:
        sent_emails = json.load(file)
        email['id'] = str(len(sent_emails) + 1)
        sent_emails.append(email)
        file.seek(0)
        json.dump(sent_emails, file, indent=4)
    
    logger.info(f'Created new email with ID: {email["id"]}')
    return {'success': True, 'id': email['id']}


def draft_ai_response(body: dict) -> dict:
    """
    Drafts an email using the Anthropic API.
    """
    assert type(body.get('email', None)) == dict, 'Email body must be a dictionary'
    assert len(body['email'].get('body', '')) > 0, 'Email body cannot be empty'
    
    practitioner_notes = body.get('practitioner_notes', '')
    if len(practitioner_notes) > 0:
        practitioner_notes = PROMPT_NOTES.replace('{{PRACTITIONER_NOTES}}', practitioner_notes)
    
    prompt = PROMPT_BODY \
            .replace('{{SUBJECT}}', body['email'].get('subject', 'No Subject')) \
            .replace('{{BODY}}', body['email']['body']) \
            .replace('{{NOTES}}', practitioner_notes)
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL"),
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response
