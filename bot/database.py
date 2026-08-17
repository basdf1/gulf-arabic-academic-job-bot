import sqlite3
from pathlib import Path
from datetime import datetime


# Database location
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "jobs.db"


def get_connection():
    """
    Create a connection to the SQLite database.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def init_database():
    """
    Create the jobs table if it doesn't already exist.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,
            organization TEXT,
            country TEXT,
            city TEXT,

            source TEXT,
            job_url TEXT UNIQUE,
            application_url TEXT,

            posted_date TEXT,
            deadline TEXT,

            status TEXT,

            first_seen TEXT NOT NULL,
            last_checked TEXT NOT NULL,

            notified INTEGER DEFAULT 0
        )
        """
    )

    connection.commit()

    connection.close()


def job_exists(job_url):
    """
    Check whether a job URL already exists.
    """

    if not job_url:
        return False

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM jobs
        WHERE job_url = ?
        """,
        (job_url,),
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None


def add_job(
    title,
    organization,
    country,
    city,
    source,
    job_url,
    application_url=None,
    posted_date=None,
    deadline=None,
    status="UNKNOWN",
):
    """
    Add a new job to the database.
    """

    if not job_url:
        return None

    if job_exists(job_url):
        return None

    now = datetime.utcnow().isoformat()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO jobs (
            title,
            organization,
            country,
            city,
            source,
            job_url,
            application_url,
            posted_date,
            deadline,
            status,
            first_seen,
            last_checked,
            notified
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
        (
            title,
            organization,
            country,
            city,
            source,
            job_url,
            application_url,
            posted_date,
            deadline,
            status,
            now,
            now,
        ),
    )

    connection.commit()

    job_id = cursor.lastrowid

    connection.close()

    return job_id


def update_job_status(job_url, status, deadline=None):
    """
    Update the current application status.
    """

    if not job_url:
        return

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.utcnow().isoformat()

    cursor.execute(
        """
        UPDATE jobs
        SET
            status = ?,
            deadline = COALESCE(?, deadline),
            last_checked = ?
        WHERE job_url = ?
        """,
        (
            status,
            deadline,
            now,
            job_url,
        ),
    )

    connection.commit()

    connection.close()


def mark_notified(job_url):
    """
    Mark a job as already sent to Telegram.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE jobs
        SET notified = 1
        WHERE job_url = ?
        """,
        (job_url,),
    )

    connection.commit()

    connection.close()


def get_unnotified_open_jobs():
    """
    Return jobs that:
    - are confirmed OPEN
    - have not been sent yet
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM jobs
        WHERE status = 'OPEN'
        AND notified = 0
        ORDER BY first_seen DESC
        """
    )

    jobs = cursor.fetchall()

    connection.close()

    return jobs


def get_open_jobs():
    """
    Return all currently open jobs.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM jobs
        WHERE status = 'OPEN'
        ORDER BY last_checked DESC
        """
    )

    jobs = cursor.fetchall()

    connection.close()

    return jobs
