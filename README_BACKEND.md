# Beauty Parlour Backend (FastAPI + SQLite)

This is a modern Python-based backend for the Beauty Parlour project.

## Setup Instructions

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```
   - The server will start on `http://localhost:5000`.
   - A database file named `beauty_parlour.db` will be created automatically.

## API Documentation
Access the interactive docs at:
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

## Features
- **FastAPI**: High performance, easy to use.
- **SQLite**: No setup required, zero configuration.
- **Auto-seeding**: Automatically seeds initial services on first run.
