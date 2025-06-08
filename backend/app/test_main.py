import pytest
from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_index_emails_success(monkeypatch):
    monkeypatch.setattr("app.main.get_emails", lambda: [{"id": "1", "from": "a@b.com", "patient_name": "Pat", "subject": "Test"}])
    response = client.get("/emails")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["id"] == "1"


def test_index_emails_failure(monkeypatch):
    monkeypatch.setattr("app.main.get_emails", lambda: (_ for _ in ()).throw(Exception("fail")))
    response = client.get("/emails")
    assert response.status_code == 500


def test_get_email_success(monkeypatch):
    monkeypatch.setattr("app.main.get_email_by_id", lambda eid: {"id": eid, "from": "a@b.com", "patient_name": "Pat", "subject": "Test"})
    response = client.get("/emails/123")
    assert response.status_code == 200
    assert response.json()["id"] == "123"


def test_get_email_not_found(monkeypatch):
    monkeypatch.setattr("app.main.get_email_by_id", lambda eid: None)
    response = client.get("/emails/999")
    assert response.status_code == 404


def test_get_email_invalid(monkeypatch):
    def raise_assertion_error(eid): raise AssertionError("bad id")
    monkeypatch.setattr("app.main.get_email_by_id", raise_assertion_error)
    response = client.get("/emails/bad")
    assert response.status_code == 400


def test_post_email_success(monkeypatch):
    monkeypatch.setattr("app.main.create_reply", lambda body, eid: None)
    response = client.post("/emails/1/reply", json={"to": "a@b.com", "body": "hi"})
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_post_email_invalid(monkeypatch):
    def raise_assertion_error(body, eid): raise AssertionError("bad data")
    monkeypatch.setattr("app.main.create_reply", raise_assertion_error)
    response = client.post("/emails/1/reply", json={"to": "a@b.com", "body": "hi"})
    assert response.status_code == 400


def test_post_email_failure(monkeypatch):
    def raise_exception(body, eid): raise Exception("fail")
    monkeypatch.setattr("app.main.create_reply", raise_exception)
    response = client.post("/emails/1/reply", json={"to": "a@b.com", "body": "hi"})
    assert response.status_code == 500


def test_post_ai_email_drafting_success(monkeypatch):
    monkeypatch.setattr("app.main.draft_ai_response", lambda body: {"reply": "AI draft"})
    response = client.post("/generate-reply", json={"email": {}, "practitioners_notes": ""})
    assert response.status_code == 200
    assert response.json()["data"]["reply"] == "AI draft"


def test_post_ai_email_drafting_assertion(monkeypatch):
    def raise_assertion(body): raise AssertionError("bad input")
    monkeypatch.setattr("app.main.draft_ai_response", raise_assertion)
    response = client.post("/generate-reply", json={"email": {}, "practitioners_notes": ""})
    assert response.status_code == 400


def test_post_ai_email_drafting_failure(monkeypatch):
    def raise_exception(body): raise Exception("fail")
    monkeypatch.setattr("app.main.draft_ai_response", raise_exception)
    response = client.post("/generate-reply", json={"email": {}, "practitioners_notes": ""})
    assert response.status_code == 500
