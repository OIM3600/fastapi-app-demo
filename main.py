import sqlite3
from contextlib import contextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# 1. FastAPI initialization
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Database configuration
INSTANCE_PATH = Path("instance")
INSTANCE_PATH.mkdir(exist_ok=True)
DATABASE = INSTANCE_PATH / "database.db"


# 3. Database initialization
def init_db():
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """
        )
        db.commit()


# 4. Thread-safe database connection management
@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# 5. Route definitions
@app.get("/")
async def index(request: Request):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return templates.TemplateResponse(
            "index.html", {"request": request, "users": users}
        )


@app.post("/add")
async def add_user(name: str = Form(...), email: str = Form(...)):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)", (name, email)
        )
        db.commit()
        return RedirectResponse(url="/", status_code=303)


# 6. Initialize the database
init_db()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
