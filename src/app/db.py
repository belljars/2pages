import os
import sqlite3
from datetime import datetime, timezone

DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'archive.db')
)
DB_PATH = os.path.abspath(os.environ.get('TWOPAGES_DB_PATH', DEFAULT_DB_PATH))


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                type     TEXT    NOT NULL,
                content  TEXT    NOT NULL,
                filename TEXT,
                mimetype TEXT,
                added_at TEXT    NOT NULL
            )
        ''')


def add_entry(type_, content, filename=None, mimetype=None):
    added_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            'INSERT INTO entries (type, content, filename, mimetype, added_at) VALUES (?, ?, ?, ?, ?)',
            (type_, content, filename, mimetype, added_at),
        )
        return cursor.lastrowid


def get_entries():
    with get_connection() as conn:
        rows = conn.execute('SELECT * FROM entries ORDER BY id').fetchall()
    return [dict(row) for row in rows]


def get_count():
    with get_connection() as conn:
        return conn.execute('SELECT COUNT(*) FROM entries').fetchone()[0]
