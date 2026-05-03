---
mode: agent
description: After merging the release PR, creates the tag and triggers the GitHub Actions build
tools:
  - githubRepo
  - terminalLastCommand
  - runCommand
---

You are helping publish a new release for the Game Save Backup Manager project.

## Context

The release PR has already been merged into `main`. Your job is to:
1. Pull the latest `main`
2. Read the current version from `src/version.py`
3. Confirm the tag with the user
4. Create and push the tag to trigger GitHub Actions

## Steps

```bash
# Pull latest main
git checkout main
git pull origin main
```

Then read `src/version.py` and extract `APP_VERSION`.

Show the user:
- Current version: `{VERSION}`
- Tag to be created: `v{VERSION}`

Ask for confirmation before continuing.

```bash
# Check if tag already exists
git tag -l v{VERSION}
```

If the tag already exists, stop and tell the user. Do not proceed.

If the tag does not exist:

```bash
# Create and push tag
git tag v{VERSION}
git push origin v{VERSION}
```

## After finishing

Tell the user:
- Tag `v{VERSION}` was pushed successfully
- GitHub Actions is now building `GameBackupManager.exe`
- They can follow the build at: https://github.com/814942/backup-manager/actions
- When the build finishes, the `.exe` will be attached to the release at: https://github.com/814942/backup-manager/releases

## Rules

- Never create a tag if one already exists for this version
- Never push to `main` directly
- Always confirm the tag name with the user before pushing
- If any step fails, stop and explain clearly what went wrong