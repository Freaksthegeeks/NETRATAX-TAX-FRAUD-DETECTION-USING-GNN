import sqlite3
from pathlib import Path
import threading
import time

DB_PATH = Path(__file__).parent.parent / "data" / "uploads" / "db.sqlite3"
_lock = threading.Lock()

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _lock, sqlite3.connect(str(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                filepath TEXT,
                uploaded_at TEXT,
                uploader TEXT,
                filetype TEXT,
                rows INTEGER,
                columns INTEGER,
                encrypted INTEGER DEFAULT 0
            )
        ''')
        # Ensure encrypted column exists for older DBs
        cur.execute("PRAGMA table_info(uploads)")
        cols = [r[1] for r in cur.fetchall()]
        if 'encrypted' not in cols:
            try:
                cur.execute("ALTER TABLE uploads ADD COLUMN encrypted INTEGER DEFAULT 0")
            except Exception:
                pass
        conn.commit()

def record_upload(filename, filepath, uploader="anonymous", filetype="csv", rows=None, columns=None, encrypted: int = 0):
    """Record an upload into the uploads DB.

    encrypted: 0 or 1 flag indicating whether the stored file is encrypted
    """
    init_db()
    uploaded_at = time.strftime("%Y-%m-%d %H:%M:%S")
    with _lock, sqlite3.connect(str(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO uploads (filename, filepath, uploaded_at, uploader, filetype, rows, columns, encrypted) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (filename, str(filepath), uploaded_at, uploader, filetype, rows, columns, int(bool(encrypted)))
        )
        conn.commit()
        return cur.lastrowid

def list_uploads(limit=50):
    init_db()
    with _lock, sqlite3.connect(str(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, filename, filepath, uploaded_at, uploader, filetype, rows, columns, encrypted FROM uploads ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        return [dict(id=r[0], filename=r[1], filepath=r[2], uploaded_at=r[3], uploader=r[4], filetype=r[5], rows=r[6], columns=r[7], encrypted=bool(r[8])) for r in rows]
