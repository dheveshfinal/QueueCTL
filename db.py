import sqlite3
import uuid
from datetime import datetime

DB_NAME = "queue.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        command TEXT NOT NULL,
        state TEXT DEFAULT 'pending',
        attempts INTEGER DEFAULT 0,
        max_retries INTEGER DEFAULT 3,
        priority INTEGER DEFAULT 0,
        timeout INTEGER DEFAULT 10,
        run_at TEXT DEFAULT NULL,
        created_at TEXT,
        updated_at TEXT
    )
    """)

 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT,
        attempt INTEGER,
        exit_code INTEGER,
        stdout TEXT,
        stderr TEXT,
        started_at TEXT,
        finished_at TEXT
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()

def get_config(key, default=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM config WHERE key=?", (key,))
    row = cur.fetchone()
    conn.close()
    return row["value"] if row else default

def set_config(key, value):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def add_job(command, max_retries=3, priority=0, timeout=10, run_at=None):
    conn = get_connection()
    cursor = conn.cursor()
    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    cursor.execute("""
    INSERT INTO jobs (id, command, state, attempts, max_retries, priority, timeout, run_at, created_at, updated_at)
    VALUES (?, ?, 'pending', 0, ?, ?, ?, ?, ?, ?)
    """, (job_id, command, max_retries, priority, timeout, run_at, now, now))
    conn.commit()
    conn.close()
    return job_id

def get_next_job():
    conn = get_connection()
    cursor = conn.cursor()

    conn.execute("BEGIN IMMEDIATE")

    cursor.execute("""
        SELECT * FROM jobs
        WHERE state = 'pending'
          AND (run_at IS NULL OR datetime(run_at) <= datetime('now'))
        ORDER BY priority DESC, created_at ASC
        LIMIT 1
    """)
    job = cursor.fetchone()

    if job:
        cursor.execute("UPDATE jobs SET state='locked', updated_at=? WHERE id=?",
                       (datetime.utcnow().isoformat(), job["id"]))
        conn.commit()

    conn.close()
    return job


def update_job_state(job_id, new_state, attempts=None):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    if attempts is not None:
        cursor.execute("UPDATE jobs SET state=?, attempts=?, updated_at=? WHERE id=?",
                       (new_state, attempts, now, job_id))
    else:
        cursor.execute("UPDATE jobs SET state=?, updated_at=? WHERE id=?",
                       (new_state, now, job_id))
    conn.commit()
    conn.close()

def add_log(job_id, attempt, exit_code, stdout, stderr, started_at, finished_at):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO job_logs (job_id, attempt, exit_code, stdout, stderr, started_at, finished_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (job_id, attempt, exit_code, stdout, stderr, started_at, finished_at))
    conn.commit()
    conn.close()

def list_jobs(state=None):
    conn = get_connection()
    cursor = conn.cursor()
    if state:
        cursor.execute("SELECT * FROM jobs WHERE state=?", (state,))
    else:
        cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_metrics():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT state, COUNT(*) AS count FROM jobs GROUP BY state")
    job_counts = {row["state"]: row["count"] for row in cur.fetchall()}

    cur.execute("""
    SELECT AVG(julianday(finished_at) - julianday(started_at)) * 86400 AS avg_runtime
    FROM job_logs
    WHERE finished_at IS NOT NULL AND started_at IS NOT NULL
    """)
    row = cur.fetchone()
    avg_runtime = row["avg_runtime"] if row and row["avg_runtime"] is not None else 0

    conn.close()
    return {"job_counts": job_counts, "avg_runtime": avg_runtime}
