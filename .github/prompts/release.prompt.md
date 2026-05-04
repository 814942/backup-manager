---
description: Creates a release branch, bumps version, and opens a PR on GitHub
---

You are helping create a new release for the Game Save Backup Manager project.

## Your job

1. Read the current version from `src/version.py` using the GitHub MCP
2. Ask the user what the new version should be (e.g. 1.1.0)
3. Confirm the plan before doing anything
4. Execute the following steps in order using the GitHub MCP:

## Steps

**1. Create the branch**
Use GitHub MCP to create branch `release/v{NEW_VERSION}` from the latest commit SHA of `main`.

**2. Bump version**
Use GitHub MCP to update `src/version.py` on branch `release/v{NEW_VERSION}`.
Replace `APP_VERSION = "..."` with `APP_VERSION = "{NEW_VERSION}"`.
Commit message: `chore: release v{NEW_VERSION}`.

**3. Open the PR**
Use GitHub MCP to create a PR:
- From: `release/v{NEW_VERSION}`
- To: `main`
- Title: `Release v{NEW_VERSION}`
- Body: `Automated release PR.\n\nAfter merging, GitHub Actions will tag and build the .exe automatically.`

## After finishing

Tell the user:
- The PR URL to review and merge
- That once merged, GitHub Actions handles the tag and .exe build — no further steps needed

## Rules

- Never push directly to `main`
- Never create the tag — Actions handles that after merge
- If any step fails, stop and explain what went wrong clearly
- Always confirm the plan with the user before executing any MCP call