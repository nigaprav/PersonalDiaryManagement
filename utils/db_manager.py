# utils/db_manager.py
import os
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from zoneinfo import ZoneInfo
# Load local .env (for local dev)
load_dotenv()

# 1) Prefer environment variable (or .env)
DB_URL = os.getenv("DATABASE_URL")

# 2) If running inside Streamlit and env var missing, try st.secrets
if not DB_URL:
    try:
        import streamlit as _st
        DB_URL = _st.secrets.get("DATABASE_URL")
    except Exception:
        pass

if not DB_URL:
    raise RuntimeError("DATABASE_URL not set. Put it in .env or Streamlit secrets.")

def get_conn():
    return psycopg2.connect(DB_URL)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


# --- user/entry helpers (same as your app expects) ---
def register_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        c.close()
        conn.close()
        return False
    c.close()
    conn.close()
    return True


def login_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE username=%s AND password=%s", (username, password))
    user = c.fetchone()
    c.close()
    conn.close()
    return user


def add_entry(user_id, title, content):
    conn = get_conn()
    c = conn.cursor()
    timestamp = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y, %I:%M %p")
    c.execute("INSERT INTO entries (user_id, title, content, timestamp) VALUES (%s, %s, %s, %s)",
              (user_id, title, content, timestamp))
    conn.commit()
    c.close()
    conn.close()


def get_entries(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, title, content, timestamp FROM entries WHERE user_id=%s ORDER BY id DESC", (user_id,))
    entries = c.fetchall()
    c.close()
    conn.close()
    return entries


def update_entry(entry_id, new_title, new_content):
    conn = get_conn()
    c = conn.cursor()
    timestamp = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y, %I:%M %p")
    c.execute("UPDATE entries SET title=%s, content=%s, timestamp=%s WHERE id=%s",
              (new_title, new_content, timestamp, entry_id))
    conn.commit()
    c.close()
    conn.close()


def delete_entry(entry_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE id=%s", (entry_id,))
    conn.commit()
    c.close()
    conn.close()
