Phase 1: Repository Metadata

Start with understanding the repository.

Questions you should be able to answer:

Does the repository exist?
Who owns it?
What is the default branch?
Is it public or private?
What language does it primarily use?

This is all available from the Repository endpoint.

Phase 2: Workflows

Next, SpriteSRE needs to know:

What workflows are present?
What are their names?
What is their workflow ID?

This comes from the Actions Workflows endpoints.

Phase 3: Workflow Runs

This is where your project really starts.

You want information like:

Latest workflow runs
Status (queued, in_progress, completed)
Conclusion (success, failure, cancelled, etc.)
Trigger event (push, pull_request, etc.)
Branch
Commit SHA
Run ID

The Run ID is especially important because it becomes the key to fetching jobs and logs later.

Phase 4: Jobs

A workflow can have multiple jobs.

For example:

CI Pipeline
├── Build ✅
├── Lint ❌
└── Test ⏳

You'll eventually need to know:

Which job failed?
How long did it run?
What runner executed it?
Phase 5: Logs

This is the endpoint SpriteSRE ultimately cares about.

Given a failed workflow run, can you retrieve its logs?

Everything after this—AI diagnosis, context building, patch generation—depends on these logs.