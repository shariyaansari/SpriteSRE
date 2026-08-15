
# ? For testing, the cleanest way to verify this without wiring it into the full webhook flow yet is a small standalone script that: authenticates, calls get_jobs, filters with get_failed_jobs, then iterates and calls get_failed_steps per job, printing exactly the fields listed

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]

# Keep the project root on sys.path for `backend.*` imports, but do not leave the
# internal `backend` directory on the path. That directory contains a package named
# `queue`, which shadows Python's standard-library `queue` module used by httpx/anyio.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

for shadow_path in (str(BACKEND_DIR), str(BACKEND_DIR / "scripts")):
    if shadow_path in sys.path:
        sys.path.remove(shadow_path)

from backend.config import settings
from backend.github.client import GitHubClient


async def main() -> None:
    client = GitHubClient()

    owner = "shariyaansari"
    repo = "SpriteSRE"
    run_id = 31796471903  # replace with your actual failed run ID

    jobs = await client.get_jobs(owner, repo, run_id)
    failed_jobs = client.get_failed_jobs(jobs)

    if not failed_jobs:
        print("No failed jobs found.")
        return

    for job in failed_jobs:
        print(f"Failed Job: {job['name']} (id={job['id']}, conclusion={job['conclusion']})")

        failed_steps = client.get_failed_steps(job)

        for step in failed_steps:
            print(
                f"  Failed Step: {step['name']} "
                f"(number={step['number']}, conclusion={step['conclusion']}, "
                f"started_at={step['started_at']}, completed_at={step['completed_at']})"
            )


if __name__ == "__main__":
    asyncio.run(main())