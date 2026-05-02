from app.tests.conftest import mock_s3, client
import pytest
from io import BytesIO


# Unit tests
def test_validate_size_too_large():
    from apps.api.app.services.file_validation import validator
    from unittest.mock import MagicMock

    mock_file = MagicMock()
    mock_file.file.tell.return_value = 20 * 1024 * 1024

    with pytest.raises(ValueError, match="larger than 10mb"):
        validator.validate_size(mock_file)


# Integration testing the endpoint
def test_upload_endpoint_success(client, mock_s3, db_session):
    # Prepare a fake pdf
    file_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    file_name = "test_medical.pdf"

    response = client.post(
        "/api/v1/upload",
        files = {"file": (file_name, file_content, "application/pdf")},
        data={"patient_id": "123", "priority": "1"}
    )

    assert response.status_code == 200
    data = response.json()
    assert response.json()["message"] == "Job Created Successfully"
    assert "job_id" in data

     # Senior verification: Ensure upload_fileobj was called correctly
    # Note: run_in_threadpool executes this, so we check the mock's call history
    mock_s3.upload_fileobj.assert_called_once() # Verify s3 was actually hit