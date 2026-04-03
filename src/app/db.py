import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'archive.db'))


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


def get_entry(page):
    with get_connection() as conn:
        row = conn.execute('SELECT * FROM entries WHERE id = ?', (page,)).fetchone()
    return dict(row) if row else None


def get_count():
    with get_connection() as conn:
        return conn.execute('SELECT COUNT(*) FROM entries').fetchone()[0]
