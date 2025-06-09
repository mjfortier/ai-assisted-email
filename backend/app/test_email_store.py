import pytest
import json
from unittest.mock import patch, mock_open
from .email_store import (
    get_emails,
    _get_replies,
    get_email_by_id,
    create_reply,
    draft_ai_response,
)

MOCK_EMAILS = json.dumps([
    {"id": "1", "from": "a@b.com", "patient_name": "Pat", "subject": "Test", "body": "Hello"},
    {"id": "2", "from": "b@b.com", "patient_name": "Sam", "subject": "Hi", "body": "Hi there"}
])
MOCK_SENT = json.dumps([
    {"id": "1", "to": "a@b.com", "body": "Reply", "parent": "1"}
])

def test_get_emails():
    with patch("builtins.open", mock_open(read_data=MOCK_EMAILS)):
        emails = get_emails()
        assert isinstance(emails, list)
        assert len(emails) == 2
        assert emails[0]["id"] == "1"
        assert "body" not in emails[0]


def test_get_replies():
    with patch("builtins.open", mock_open(read_data=MOCK_SENT)):
        replies = _get_replies("1")
        assert isinstance(replies, list)
        assert replies[0]["parent"] == "1"


def test_get_email_by_id_found():
    with patch("builtins.open", mock_open(read_data=MOCK_EMAILS)):
        email = get_email_by_id("1")
        assert email["id"] == "1"
        assert "replies" in email


def test_get_email_by_id_not_found():
    with patch("builtins.open", mock_open(read_data=MOCK_EMAILS)):
        email = get_email_by_id("999")
        assert email is None


def test_get_email_by_id_assertion():
    with pytest.raises(AssertionError):
        get_email_by_id("")


def test_create_reply_success():
    sent_emails = []

    def fake_json_load(file):
        return sent_emails.copy()
    
    def fake_json_dump(data, file, indent):
        sent_emails.clear()
        sent_emails.extend(data)
    
    with patch("builtins.open", mock_open(read_data="[]")):
        with patch("json.load", fake_json_load), patch("json.dump", fake_json_dump):
            result = create_reply({"to": "a@b.com", "body": "Hello"}, "1")
            assert result["success"]
            assert sent_emails[0]["parent"] == "1"


def test_create_reply_invalid_email():
    with pytest.raises(AssertionError):
        create_reply({"to": "not-an-email", "body": "Hello"}, "1")


def test_create_reply_empty_body():
    with pytest.raises(AssertionError):
        create_reply({"to": "a@b.com", "body": ""}, "1")


def test_draft_ai_response_success(monkeypatch):
    # Mock out the Anthropic SDK
    class FakeAnthropic:
        class messages:
            @staticmethod
            def create(model, max_tokens, messages):
                class Resp:
                    content = [type("T", (), {"text": "<response_email>Drafted reply</response_email>"})()]
                return Resp()
    monkeypatch.setattr("anthropic.Anthropic", lambda api_key: FakeAnthropic)
    
    body = {"email": {"body": "Hello", "subject": "Test"}, "practitioner_notes": "note"}
    result = draft_ai_response(body)
    assert "reply" in result
    assert "Drafted reply" in result["reply"]


def test_draft_ai_response_assertion():
    with pytest.raises(AssertionError):
        draft_ai_response({"email": "notadict"})
    with pytest.raises(AssertionError):
        draft_ai_response({"email": {"body": ""}})
