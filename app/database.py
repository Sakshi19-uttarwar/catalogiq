import os
import sqlite3
from typing import Generator

DB_PATH = os.getenv("DATABASE_PATH", "catalogiq.db")

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db() -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        total INTEGER NOT NULL DEFAULT 0,
        done INTEGER NOT NULL DEFAULT 0,
        failed INTEGER NOT NULL DEFAULT 0,
        cache_hits INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        started_at TEXT,
        finished_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        sku TEXT PRIMARY KEY,
        raw_title TEXT NOT NULL,
        raw_description TEXT,
        clean_title TEXT,
        category TEXT,
        brand TEXT,
        tags TEXT,
        status TEXT NOT NULL,
        error TEXT,
        content_hash TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS content_cache (
        content_hash TEXT PRIMARY KEY,
        clean_title TEXT NOT NULL,
        category TEXT NOT NULL,
        brand TEXT,
        tags TEXT NOT NULL
    )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_hash ON products(content_hash);")

    conn.commit()
    conn.close()

def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
