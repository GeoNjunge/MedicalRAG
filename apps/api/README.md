## 🧪 Running the Redesigned Backend Locally

### 1️⃣ Clone the repository (if not already)

```bash
git clone <your-repo-url>
cd /apps/api
```

---

### 2️⃣ Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux / macOS
# venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4️⃣ Set up environment variables

Create a `.env` file in the root of `redesigned_backend` with placeholders:

```env
DATABASE_URL=your_postgres_connection_string_here
S3_BUCKET_URL=your_s3_bucket_url_here
S3_BUCKET_NAME=your_s3_bucket_name_here
S3_REGION_NAME=your_s3_region_here
AWS_ACCESS_KEY=your_aws_access_key_here
AWS_SECRET_KEY=your_aws_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
```

---

### 5️⃣ Run the FastAPI server with Uvicorn

```bash
uvicorn app.main:app --reload
```

* `app.main:app` → points to your FastAPI instance in `app/main.py`
* `--reload` → automatically reloads the server when code changes

---

### 6️⃣ Access the API

Once running, you can open your browser or Postman:

```
http://127.0.0.1:8000
```

* Docs available at:

```
http://127.0.0.1:8000/docs
```

* Alternative Swagger UI:

```
http://127.0.0.1:8000/redoc
```

---

💡 **Tip:** Always activate the virtual environment before running the server to ensure dependencies are isolated.

---
