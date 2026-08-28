import asyncio

from backend.github.client import GitHubClient


async def main():
    client = GitHubClient()

    jobs = await client.get_jobs(
        owner="shariyaansari",
        repo="SpriteSre",
        run_id=33200666888,
    )

    print("\n===== ALL JOBS =====")
    for job in jobs:
        print(
            f"ID: {job['id']}"
            f" | Name: {job['name']}"
            f" | Conclusion: {job.get('conclusion')}"
        )

    failed_jobs = client.get_failed_jobs(jobs)

    print("\n===== FAILED JOBS =====")
    for job in failed_jobs:
        print(
            f"ID: {job['id']}"
            f" | Name: {job['name']}"
            f" | Conclusion: {job.get('conclusion')}"
        )

        failed_steps = client.get_failed_steps(job)

        print("\n--- FAILED STEPS ---")
        for step in failed_steps:
            print(
                f"Name: {step['name']}"
                f" | Conclusion: {step.get('conclusion')}"
            )

        print("\n--- JOB LOG ---")
        logs = await client.get_job_logs(
            owner="shariyaansari",
            repo="SpriteSre",
            job_id=job["id"],
        )

        print(logs[:2000])

        print("\n--- EXTRACTED ERRORS ---")
        errors = client.extract_error_lines(logs)
        print(errors)

    await client.client.aclose()


if __name__ == "__main__":
    asyncio.run(main())