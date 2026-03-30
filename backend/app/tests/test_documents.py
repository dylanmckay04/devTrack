from io import BytesIO
import pytest
import app.services.r2 as r2_service


FAKE_PDF = BytesIO(b"%PDF-1.4 fake content")
FAKE_R2_KEY = "users/1/documents/fake-uuid.pdf"


@pytest.fixture(autouse=True)
def mock_r2(monkeypatch):
    """Prevent all tests in this module from making real R2 network calls."""
    async def fake_upload(file, user_id):
        return FAKE_R2_KEY

    monkeypatch.setattr(r2_service, "upload_file", fake_upload)
    monkeypatch.setattr(r2_service, "delete_file", lambda key: None)


def _pdf_file():
    """Return a fresh in-memory PDF byte stream for each upload call."""
    return ("test.pdf", BytesIO(b"%PDF-1.4 fake content"), "application/pdf")


def test_upload_document(auth_client):
    create = auth_client.post("/applications", json={
        "company": "Test Inc.",
        "role": "Backend Engineer"
    })
    app_id = create.json()["id"]
    response = auth_client.post(f"/applications/{app_id}/documents", files={"file": _pdf_file()})
    assert response.status_code == 201
    assert response.json()["filename"] == "test.pdf"
    assert response.json()["r2_key"] is not None
    assert response.json()["uploaded_at"] is not None
    assert response.json()["owner_id"] == auth_client.user.id
    assert response.json()["application_id"] == app_id

def test_get_documents(auth_client):
    create = auth_client.post("/applications", json={
        "company": "Test Inc.",
        "role": "Backend Engineer"
    })
    app_id = create.json()["id"]
    auth_client.post(f"/applications/{app_id}/documents", files={"file": _pdf_file()})
    response = auth_client.get(f"/applications/{app_id}/documents")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["filename"] == "test.pdf"
    assert response.json()[0]["r2_key"] is not None
    assert response.json()[0]["uploaded_at"] is not None
    assert response.json()[0]["owner_id"] == auth_client.user.id
    assert response.json()[0]["application_id"] == app_id

def test_delete_document(auth_client):
    create = auth_client.post("/applications", json={
        "company": "Test Inc.",
        "role": "Backend Engineer"
    })
    app_id = create.json()["id"]
    upload = auth_client.post(f"/applications/{app_id}/documents", files={"file": _pdf_file()})
    doc_id = upload.json()["id"]
    response = auth_client.delete(f"/applications/{app_id}/documents/{doc_id}")
    assert response.status_code == 204
    response = auth_client.get(f"/applications/{app_id}/documents")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_upload_rejects_invalid_content_type(auth_client):
    create = auth_client.post("/applications", json={
        "company": "Test Inc.",
        "role": "Backend Engineer"
    })
    app_id = create.json()["id"]
    response = auth_client.post(
        f"/applications/{app_id}/documents",
        files={"file": ("malware.exe", BytesIO(b"MZ fake exe"), "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]

def test_upload_rejects_oversized_file(auth_client, monkeypatch):
    # Patch MAX_UPLOAD_BYTES to a tiny limit so the test doesn't allocate 10MB
    import app.routers.documents as doc_router
    monkeypatch.setattr(doc_router, "MAX_UPLOAD_BYTES", 10)
    create = auth_client.post("/applications", json={
        "company": "Test Inc.",
        "role": "Backend Engineer"
    })
    app_id = create.json()["id"]
    response = auth_client.post(
        f"/applications/{app_id}/documents",
        files={"file": ("big.pdf", BytesIO(b"%PDF-1.4 " + b"x" * 100), "application/pdf")},
    )
    assert response.status_code == 400
    assert "too large" in response.json()["detail"]