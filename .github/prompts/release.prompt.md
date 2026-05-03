---
mode: agent
description: Creates a release branch, bumps version, and opens a PR on GitHub
tools:
  - githubRepo
  - terminalLastCommand
  - runCommand
---

You are helping create a new release for the Game Save Backup Manager project.

## Your job

1. Read the current version from `src/version.py`
2. Ask the user what the new version should be (e.g. 1.1.0)
3. Confirm the plan before doing anything
4. Execute the following steps in order:

### Steps

```bash
# Pull latest main
git checkout main
git pull origin main

# Create release branch
git checkout -b release/v{NEW_VERSION}

# Bump version in version.py
# Replace APP_VERSION = "..." with the new version

# Commit
git add src/version.py
git commit -m "chore: release v{NEW_VERSION}"

# Push branch
git push origin release/v{NEW_VERSION}
```

5. After pushing, open a PR from `release/v{NEW_VERSION}` → `main` using the GitHub CLI if available:

```bash
gh pr create \
  --title "Release v{NEW_VERSION}" \
  --body "Automated release PR.\n\nAfter merging, run the **tag** prompt to trigger the GitHub Actions build." \
  --base main \
  --head release/v{NEW_VERSION}
```

If `gh` is not available, open the browser to:
`https://github.com/814942/backup-manager/compare/main...release/v{NEW_VERSION}?quick_pull=1`

## After finishing

Tell the user:
- The PR was created (or the URL to create it manually)
- That once the PR is merged, they should run the `/tag` prompt to trigger the GitHub Actions build
- The build will produce `GameBackupManager.exe` and attach it to the release automatically

## Rules

- Never push directly to `main`
- Never create the tag before the PR is merged
- If any step fails, stop and explain what went wrong clearly
- Always confirm the plan with the user before executing