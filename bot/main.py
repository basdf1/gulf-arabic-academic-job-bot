from .database import (
    init_database,
    add_job,
    job_exists,
    update_job_status,
)

from .filters import is_relevant_job
from .checker import verify_job_application
from .sources import collect_jobs


def process_job(job):
    """
    Process one collected job.

    Pipeline:
    1. Filter
    2. Check duplicate
    3. Verify application status
    4. Save if relevant
    """

    title = job.get("title", "")
    description = job.get("description", "")
    location = job.get("country", "")
    job_url = job.get("job_url", "")

    # -------------------------
    # 1. Relevance filter
    # -------------------------

    if not is_relevant_job(
        title=title,
        description=description,
        location=location,
    ):
        return {
            "result": "REJECTED",
            "reason": "Does not match search criteria",
        }

    # -------------------------
    # 2. Duplicate check
    # -------------------------

    if job_exists(job_url):
        return {
            "result": "DUPLICATE",
            "reason": "Job already exists",
        }

    # -------------------------
    # 3. Verify application
    # -------------------------

    verification = verify_job_application(job_url)

    status = verification["status"]

    # IMPORTANT:
    # UNKNOWN is NOT treated as OPEN.

    if status != "OPEN":
        return {
            "result": status,
            "reason": "Application is not confirmed open",
        }

    # -------------------------
    # 4. Save job
    # -------------------------

    job_id = add_job(
        title=title,
        organization=job.get("organization", ""),
        country=job.get("country", ""),
        city=job.get("city", ""),
        source=job.get("source", ""),
        job_url=job_url,
        application_url=job.get(
            "application_url",
            job_url,
        ),
        posted_date=job.get("posted_date"),
        deadline=job.get("deadline"),
        status="OPEN",
    )

    if job_id is None:
        return {
            "result": "DUPLICATE",
            "reason": "Job already exists",
        }

    return {
        "result": "NEW_OPEN_JOB",
        "job_id": job_id,
    }


def run():
    """
    Main bot process.
    """

    print("=" * 60)
    print("Gulf Arabic Academic Job Bot")
    print("=" * 60)

    # Create database
    init_database()

    print("[1] Database ready")

    # Collect jobs
    jobs = collect_jobs()

    print(f"[2] Collected jobs: {len(jobs)}")

    statistics = {
        "NEW_OPEN_JOB": 0,
        "REJECTED": 0,
        "DUPLICATE": 0,
        "CLOSED": 0,
        "UNKNOWN": 0,
    }

    # Process every job
    for job in jobs:

        result = process_job(job)

        result_type = result.get("result")

        if result_type in statistics:
            statistics[result_type] += 1

        print(
            f"[JOB] {job.get('title', 'Unknown')} "
            f"-> {result_type}"
        )

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)

    for key, value in statistics.items():
        print(f"{key}: {value}")

    print("=" * 60)


if __name__ == "__main__":
    run()
