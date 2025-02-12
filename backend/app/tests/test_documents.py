def test_upload_document(client, db):
    file_data = {"pdf_file": ("test.pdf", b"Fake PDF Content", "application/pdf")}
    response = client.post("/documents/upload", files=file_data, data={"title": "Test Doc", "teacher_id": 1})
    assert response.status_code == 200
    assert response.json()["message"] == "Documento subido exitosamente"

def test_get_documents(client, db):
    response = client.get("/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
