import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "interface_manager.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn):
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS interfaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            method TEXT NOT NULL,
            path TEXT NOT NULL,
            description TEXT DEFAULT '',
            request_params TEXT DEFAULT '{}',
            response_schema TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS mock_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interface_id INTEGER NOT NULL,
            enabled INTEGER DEFAULT 0,
            status_code INTEGER DEFAULT 200,
            headers TEXT DEFAULT '{}',
            body TEXT DEFAULT '{}',
            delay_ms INTEGER DEFAULT 0,
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (interface_id) REFERENCES interfaces(id)
        );
        CREATE TABLE IF NOT EXISTS change_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interface_id INTEGER NOT NULL,
            field TEXT NOT NULL,
            old_value TEXT DEFAULT '',
            new_value TEXT DEFAULT '',
            changed_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (interface_id) REFERENCES interfaces(id)
        );
        CREATE TABLE IF NOT EXISTS integration_statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interface_id INTEGER NOT NULL,
            status TEXT DEFAULT '未开始',
            notes TEXT DEFAULT '',
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (interface_id) REFERENCES interfaces(id)
        );
    """)
    conn.commit()
