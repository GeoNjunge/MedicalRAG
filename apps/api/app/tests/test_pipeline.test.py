import pytest
from fakeredis import FakeStrictRedis
from fastapi.testclient import TestClient
from unittest.mock import patch
from rq import Queue

from apps.api.app.main import app
from apps.api.app.worker.ai_pipeline import run_ner_pipeline

# 1. Create ONE fake redis instance to be shared
fake_redis = FakeStrictRedis()
client = TestClient(app=app)

@pytest.fixture(autouse=True)
def mock_redis_connection():
    """
    This 'forces' your app to use fake_redis instead of a real one.
    Adjust 'app.api.v1.routes.upload.redis_conn' to match where your 
    actual redis_conn is defined.
    """
    with patch('app.api.v1.routes.upload.redis_conn', fake_redis), \
         patch('app.worker.worker.redis_conn', fake_redis):
        yield

@pytest.fixture
def mock_worker_dependencies():
    with patch('app.worker.ai_tasks.document_reader.extract_text_from_pdf') as mock_extract, \
         patch('app.worker.ai_tasks.disease_extractor.get_negative_entities') as mock_diseases:
        
        mock_extract.return_value = "Sample text from PDF"
        mock_diseases.return_value = {'disease': 'none'}
        yield

def test_job_polling_lifecycle(mock_worker_dependencies):
    print("\n--- REGISTERED ROUTES ---")
    for route in app.routes:
        # This will show us the EXACT strings FastAPI is looking for
        print(f"ROUTE: {route.path} | METHODS: {route.methods}")
    print("-------------------------\n")
    test_job_id = "test_123"
    
    # 2. Use the SHARED fake_redis for the queue
    q = Queue(connection=fake_redis, is_async=False)

    # 3. Enqueue and execute (is_async=False runs it immediately in this thread)
    q.enqueue(run_ner_pipeline, file_content=b"fake pdf", job_id=test_job_id)

    # 4. Call the endpoint
    response = client.get(f"/api/v1/status/{test_job_id}")

    # 5. Assertions
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == "Completed"
    assert "diseases_json" in data["result"]
