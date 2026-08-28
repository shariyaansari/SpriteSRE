import asyncio

from backend.github.client import GitHubClient


async def main():
    client = GitHubClient()

    failure_reason = await client.get_failure_reason(
        owner="shariyaansari",
        repo="SpriteSRE",
        run_id=YOUR_RUN_ID,
    )

    print("\n===== FAILURE REASON =====")
    print(failure_reason)
    print("==========================")

    await client.client.aclose()


if __name__ == "__main__":
    asyncio.run(main())