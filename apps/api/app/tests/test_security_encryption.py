from cryptography.fernet import Fernet
from sqlalchemy import text

from app.core.security_encryption import (
    decrypt_field,
    encrypt_field,
    reset_encryption_client,
)


def test_encrypt_decrypt_roundtrip(monkeypatch):
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("ENCRYPTION_KEY", key)
    reset_encryption_client()

    plaintext = "Patient has Type 2 Diabetes"
    token = encrypt_field(plaintext)

    assert token != plaintext
    assert decrypt_field(token) == plaintext


def test_decrypt_legacy_plaintext(monkeypatch):
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("ENCRYPTION_KEY", key)
    reset_encryption_client()

    legacy = "legacy-unencrypted-value"
    assert decrypt_field(legacy) == legacy


def test_encrypted_job_fields_persist_and_decrypt(db_session, monkeypatch):
    from app.models.job import Job

    key = Fernet.generate_key().decode()
    monkeypatch.setenv("ENCRYPTION_KEY", key)
    reset_encryption_client()

    job = Job(
        patient_id="PAT-001",
        input_type="pdf",
        original_filename="report.pdf",
        file_path="files/report.pdf",
        extracted_text="Confidential clinical note",
        summary_text="Summary with PHI",
        diseases_json=[{"name": "Hypertension", "icd10": "I10"}],
        labs_json=[{"test": "GLUCOSE", "value": "104"}],
    )
    db_session.add(job)
    db_session.commit()

    raw_value = db_session.execute(
        text("SELECT extracted_text FROM jobs WHERE id = :job_id"),
        {"job_id": job.id},
    ).scalar_one()

    assert raw_value != "Confidential clinical note"

    loaded = db_session.query(Job).filter(Job.id == job.id).one()
    assert loaded.extracted_text == "Confidential clinical note"
    assert loaded.diseases_json[0]["name"] == "Hypertension"
