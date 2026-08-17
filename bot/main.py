from .database import (
    init_database,
    add_job,
    job_exists,
)

from .filters import is_relevant_job
from .checker import verify_job_application
from .uaeu import collect_uaeu_jobs


def process_job(job):
    """
    Process one job through the complete pipeline.
    """

    title = job.get("title", "")
    description = job.get("description", "")
    country = job.get("country", "")
    job_url = job.get("job_url", "")

    print()
    print("-" * 60)
    print(f"JOB: {title}")
    print(f"COUNTRY: {country}")
    print(f"URL: {job_url}")

    # --------------------------------
    # 1. Check relevance
    # --------------------------------

    if not is_relevant_job(
        title=title,
        description=description,
        location=country,
    ):

        print("[FILTER] Rejected")

        return {
            "result": "REJECTED"
        }

    print("[FILTER] Relevant")

    # --------------------------------
    # 2. Check duplicate
    # --------------------------------

    if job_exists(job_url):

        print("[DATABASE] Already exists")

        return {
            "result": "DUPLICATE"
        }

    # --------------------------------
    # 3. Verify application
    # --------------------------------

    print("[CHECKER] Checking application...")

    verification = verify_job_application(
        job_url
    )

    status = verification.get(
        "status",
        "UNKNOWN"
    )

    deadline = verification.get(
        "deadline"
    )

    application_url = verification.get(
        "application_url"
    )

    reason = verification.get(
        "reason",
        ""
    )

    print(
        f"[CHECKER] Status: {status}"
    )

    if deadline:
        print(
            f"[CHECKER] Deadline: {deadline}"
        )

    print(
        f"[CHECKER] Reason: {reason}"
    )

    # --------------------------------
    # IMPORTANT:
    # UNKNOWN is NOT OPEN
    # --------------------------------

    if status != "OPEN":

        print(
            "[RESULT] Not confirmed open"
        )

        return {
            "result": status,
            "deadline": deadline,
        }

    # --------------------------------
    # 4. Save confirmed open job
    # --------------------------------

    job_id = add_job(
        title=title,
        organization=job.get(
            "organization",
            ""
        ),
        country=country,
        city=job.get(
            "city",
            ""
        ),
        source=job.get(
            "source",
            ""
        ),
        job_url=job_url,
        application_url=(
            application_url
            or job_url
        ),
        posted_date=job.get(
            "posted_date"
        ),
        deadline=deadline,
        status="OPEN",
    )

    if job_id is None:

        print(
            "[DATABASE] Could not add job"
        )

        return {
            "result": "DUPLICATE"
        }

    print(
        "[RESULT] NEW OPEN JOB!"
    )

    return {
        "result": "NEW_OPEN_JOB",
        "job_id": job_id,
        "deadline": deadline,
    }


def run():
    """
    Main bot process.
    """

    print()
    print("=" * 60)
    print(
        "GULF ARABIC ACADEMIC JOB BOT"
    )
    print("=" * 60)

    # --------------------------------
    # Database
    # --------------------------------

    init_database()

    print(
        "[DATABASE] Ready"
    )

    # --------------------------------
    # Collect UAEU jobs
    # --------------------------------

    jobs = collect_uaeu_jobs()

    print(
        f"[MAIN] Jobs collected: {len(jobs)}"
    )

    # --------------------------------
    # Statistics
    # --------------------------------

    statistics = {
        "NEW_OPEN_JOB": 0,
        "REJECTED": 0,
        "DUPLICATE": 0,
        "CLOSED": 0,
        "UNKNOWN": 0,
    }

    # --------------------------------
    # Process jobs
    # --------------------------------

    for job in jobs:

        result = process_job(job)

        result_type = result.get(
            "result",
            "UNKNOWN"
        )

        if result_type in statistics:

            statistics[result_type] += 1

    # --------------------------------
    # Final report
    # --------------------------------

    print()
    print("=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    for key, value in statistics.items():

        print(
            f"{key}: {value}"
        )

    print("=" * 60)


if __name__ == "__main__":
    run()
