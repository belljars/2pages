import os
import json
import sqlite3
from datetime import datetime, timezone

LEGACY_DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'archive.db')
)
CONFIG_PATH = os.path.join(
    os.path.expanduser(os.environ.get('XDG_CONFIG_HOME', '~/.config')),
    '2pages',
    'config.json',
)


def normalize_db_path(path):
    return os.path.abspath(os.path.expanduser(path))


def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def save_config(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def get_db_path():
    env_path = os.environ.get('TWOPAGES_DB_PATH')
    if env_path:
        return normalize_db_path(env_path)

    config_path = load_config().get('db_path')
    if isinstance(config_path, str) and config_path.strip():
        return normalize_db_path(config_path)

    return LEGACY_DEFAULT_DB_PATH


def set_default_db_path(path):
    config = load_config()
    config['db_path'] = normalize_db_path(path)
    save_config(config)


def get_connection():
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
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
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
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


def set_setting(key, value):
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            ''',
            (key, value),
        )


def get_setting(key, default=None):
    with get_connection() as conn:
        row = conn.execute(
            'SELECT value FROM settings WHERE key = ?',
            (key,),
        ).fetchone()
    if row is None:
        return default
    return row[0]
