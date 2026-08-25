PYTHONPATH=/home/ubuntu/projects/MedicalRAG:/home/ubuntu/projects/MedicalRAG/ml_core/src ../../venv/bin/python3 -m uvicorn app.main:app --reload


# Cline commands - use it at the project root
PYTHONPATH=/home/ubuntu/projects/MedicalRAG:/home/ubuntu/projects/MedicalRAG/ml_core/src venv/bin/python3 -m pytest ml_core/tests/

curl -X POST "127.0.0.1:10001/register" -H "content-type: application/json" -d '{"name":"Helde", "email":"helde@gmail.com", "phone":"011111", "password":"12345678"}'
curl -X POST "127.0.0.1:10001/verify-otp" -H "content-type: application/json" -d '{"otp":"819086", "phone":"011111"}'