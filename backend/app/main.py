from fastapi import FastAPI, HTTPException
from .email_store import get_emails, get_email_by_id, create_email, draft_ai_response
import logging
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/emails")
def index_emails():
    try:
        emails = get_emails()
    except Exception as e:
        logger.error(f'Error retrieving email list: {e}')
        raise HTTPException(status_code=500, detail='Failed to retrieve email list') from e
    
    return {'data': emails}


@app.get("/emails/{email_id}")
def get_email(email_id: str):
    try:
        email = get_email_by_id(email_id)
    except ValueError as ve:
        logger.error(f'Invalid email ID provided: {ve}')
        raise HTTPException(status_code=400, detail='Invalid email ID') from ve
    except Exception as e:
        logger.error(f'Error retrieving email with ID {email_id}: {e}')
        raise HTTPException(status_code=500, detail='Failed to retrieve email')
    if email is None:
        raise HTTPException(status_code=404, detail='Email not found')
    
    return {'data': email}


@app.post("/emails")
def post_email(body: dict):
    try:
        create_email(body)
    except ValueError as ve:
        logger.error(f'Invalid email data: {body}')
        raise HTTPException(status_code=400, detail='Invalid email data') from ve
    except Exception as e:
        logger.error(f'Error creating email: {e}')
        raise HTTPException(status_code=500, detail='Failed to create email') from e
    
    return {'success': True}


@app.post("/ai_email_drafting")
def post_ai_email_drafting(body: dict):
    try:
        response = draft_ai_response(body)
    except AssertionError as ae:
        logger.error(f'Assertion error in AI email drafting: {ae}')
        raise HTTPException(status_code=400, detail='Invalid AI email drafting request') from ae
    except Exception as e:
        logger.error(f'Error drafting email: {e}')
        raise HTTPException(status_code=500, detail='Failed to draft email') from e

    return {'data': response}
