import pytest
from unittest.mock import MagicMock


def test_validate_size_too_large():
    from app.services.file_validation import validator

    mock_file = MagicMock()
    mock_file.file.tell.return_value = 20 * 1024 * 1024

    with pytest.raises(ValueError, match="larger than 10mb"):
        validator.validate_size(mock_file)


def test_upload_endpoint_success(client, db_session, mocker):
    mocker.patch("app.services.push_job_to_redis.push_job")
    mocker.patch("app.worker.prod_tasks.schedule_prod_job")
    mocker.patch("app.services.file_validation.validator.validate_pdf", return_value=None)
    mocker.patch(
        "app.services.file_validation.validator.compute_hash",
        return_value="abc123",
    )

    file_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    file_name = "test_medical.pdf"

    response = client.post(
        "/api/v1/upload",
        files={"file": (file_name, file_content, "application/pdf")},
        data={"patient_id": "123", "priority": "1"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Job Created Successfully"
    assert "job_id" in data


def test_stream_job_events_not_found(client, db_session):
    response = client.get("/api/v1/jobs/nonexistent-job-id/events")
    assert response.status_code == 404
