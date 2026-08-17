print(">>> MAIN.PY LOADED <<<", flush=True)

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

    print(flush=True)
    print("-" * 60, flush=True)
    print(f"JOB: {title}", flush=True)
    print(f"COUNTRY: {country}", flush=True)
    print(f"URL: {job_url}", flush=True)

    # --------------------------------
    # 1. Check relevance
    # --------------------------------

    if not is_relevant_job(
        title=title,
        description=description,
        location=country,
    ):

        print(
            "[FILTER] Rejected",
            flush=True,
        )

        return {
            "result": "REJECTED"
        }

    print(
        "[FILTER] Relevant",
        flush=True,
    )

    # --------------------------------
    # 2. Check duplicate
    # --------------------------------

    if job_exists(job_url):

        print(
            "[DATABASE] Already exists",
            flush=True,
        )

        return {
            "result": "DUPLICATE"
        }

    # --------------------------------
    # 3. Verify application
    # --------------------------------

    print(
        "[CHECKER] Checking application...",
        flush=True,
    )

    verification = verify_job_application(
        job_url
    )

    status = verification.get(
        "status",
        "UNKNOWN",
    )

    deadline = verification.get(
        "deadline"
    )

    application_url = verification.get(
        "application_url"
    )

    reason = verification.get(
        "reason",
        "",
    )

    print(
        f"[CHECKER] Status: {status}",
        flush=True,
    )

    if deadline:

        print(
            f"[CHECKER] Deadline: {deadline}",
            flush=True,
        )

    print(
        f"[CHECKER] Reason: {reason}",
        flush=True,
    )

    # --------------------------------
    # IMPORTANT:
    # UNKNOWN is NOT OPEN
    # --------------------------------

    if status != "OPEN":

        print(
            "[RESULT] Not confirmed open",
            flush=True,
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
            "",
        ),
        country=country,
        city=job.get(
            "city",
            "",
        ),
        source=job.get(
            "source",
            "",
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
            "[DATABASE] Could not add job",
            flush=True,
        )

        return {
            "result": "DUPLICATE"
        }

    print(
        "[RESULT] NEW OPEN JOB!",
        flush=True,
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

    print(flush=True)
    print(
        "=" * 60,
        flush=True,
    )

    print(
        "GULF ARABIC ACADEMIC JOB BOT",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )

    # --------------------------------
    # Database
    # --------------------------------

    init_database()

    print(
        "[DATABASE] Ready",
        flush=True,
    )

    # --------------------------------
    # Collect UAEU jobs
    # --------------------------------

    print(
        "[MAIN] Starting UAEU collector...",
        flush=True,
    )

    jobs = collect_uaeu_jobs()

    print(
        f"[MAIN] Jobs collected: {len(jobs)}",
        flush=True,
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
            "UNKNOWN",
        )

        if result_type in statistics:

            statistics[result_type] += 1

    # --------------------------------
    # Final report
    # --------------------------------

    print(flush=True)

    print(
        "=" * 60,
        flush=True,
    )

    print(
        "FINAL RESULT",
        flush=True,
    )

    print(
        "=" * 60,
        flush=True,
    )

    for key, value in statistics.items():

        print(
            f"{key}: {value}",
            flush=True,
        )

    print(
        "=" * 60,
        flush=True,
    )


if __name__ == "__main__":
    run()
