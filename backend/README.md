# PropConnect API

Create a MySQL database named `propconnect`, copy `.env.example` to `.env`, and install dependencies with `pip install -r requirements.txt`. Run with `uvicorn app.main:app --reload --port 8000` from this folder.

For a zero-setup demo, omit `DATABASE_URL`; the service uses a local SQLite file while preserving the same table schema. Swagger docs are available at `/docs`.
