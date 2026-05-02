**Game Save Backup Manager**

Product Requirements Document (PRD)

v1.0  —  2026-05-02

# **1\. Overview**

Game Save Backup Manager is a desktop application for Windows that lets non-technical users back up and restore save files for any PC game. The user configures which folder contains the save, where to store backups, and from there the entire workflow is point-and-click — no terminal, no scripts, no technical knowledge required.

The project originated as a pair of PowerShell scripts (backup\_zomboid.ps1 / restore\_zomboid.ps1) built for Project Zomboid. The app generalizes that logic into a reusable, friendly tool that works for any game.

# **2\. Problem Statement**

PC game saves are fragile. A bad update, a corrupted file, or an accidental overwrite can wipe hours of progress. The existing solutions are:

* Manual copy-paste — error-prone, easy to forget, hard to organize

* PowerShell scripts — functional but inaccessible to non-technical users

* Cloud sync (Steam Cloud, etc.) — not available for all games, not user-controlled

There is no simple, game-agnostic desktop tool that a non-technical user can download and use in under a minute.

# **3\. Goals & Non-Goals**

## **Goals**

* Any user can back up and restore a game save without opening a terminal

* Works with any game — the user points the app to the save folder

* Distributable as a single .exe with no installation or dependencies required

* Clear, readable UI — list of backups with name, date, and size

* Safe restore — always asks for confirmation before overwriting

## **Non-Goals (v1.0)**

* Cloud storage or remote backups

* Automatic scheduled backups

* Support for macOS or Linux

* Game detection / auto-discovery of save locations

* Compression or encryption of backups

# **4\. Target Users**

Primary: PC gamers with little or no technical background. They know how to download a file and double-click it, but are not comfortable with the command line.

Secondary: Power users (like the original author) who want a faster, GUI-based alternative to running scripts manually.

# **5\. Features — v1.0 Scope**

## **F1 — Game Configuration**

The user registers one or more games. Each game has:

* A display name (e.g. 'Project Zomboid — ARK server')

* A source path: the folder that contains the active save

* A backup path: where backups for this game will be stored

Configuration is persisted in a local config.json file next to the executable. Paths are selected via the OS file picker — the user never types a path manually.

## **F2 — Backup**

For a selected game, the app copies the source folder into the backup path. The backup folder is named:

| \<original\_folder\_name\>-YYYYMMDD\_HHmmss |
| :---- |

After the copy completes, the app shows: start time, end time, duration, and size of the backup created.

## **F3 — Restore**

The app lists all available backups for the selected game, sorted newest first. Each row shows the backup name, date/time, and size. The user selects one and confirms. The app then:

1. Deletes the current active save folder

2. Copies the selected backup into its place

3. Shows a completion summary (duration, size)

| ⚠  Restore is destructive. A confirmation dialog must be shown before any files are deleted. |
| :---- |

## **F4 — Backup List**

A panel showing all backups for the currently selected game. Each entry shows: name, date, size. The list updates after every backup or delete operation.

## **F5 — Delete Old Backups**

The user can select one or more backups from the list and delete them. A confirmation dialog is shown. Bulk delete is supported (e.g. select all, delete all except the last N).

## **F6 — Settings**

A settings screen where the user can:

* Add, edit, or remove games

* Change the backup destination path for any game

* See the config.json location

# **6\. UX Requirements**

The app must be usable by someone who has never used a backup tool before. Specific requirements:

* No terminal, no scripts, no manual path typing

* All folder selection via OS native file picker

* All destructive actions (restore, delete) require an explicit confirmation dialog

* Progress must be visible during copy operations (progress bar or status text)

* Errors must be shown in plain language, not stack traces

* The app must work offline — no internet connection required

* First-run experience: if no games are configured, show a prompt to add one

# **7\. Data Model**

A single config.json persisted next to the .exe:

| {   "games": \[     {       "id": "uuid-v4",       "name": "Project Zomboid — ARK server",       "source\_path": "C:\\\\Users\\\\px005\\\\Zomboid\\\\Saves\\\\Sandbox\\\\ARK\_v1.4.0\_...",       "backup\_path": "C:\\\\Users\\\\px005\\\\Zomboid\\\\Saves\\\\Sandbox\\\\save"     }   \] } |
| :---- |

No database required. No server. Everything is local.

# **8\. Screen Inventory**

| Screen | Description |
| :---- | :---- |
| Main | Game selector (left panel) \+ backup list (right panel) \+ action buttons (Backup, Restore, Delete) |
| Settings | Add / edit / remove games. Each game: name, source path, backup path. |
| Confirm Dialog | Modal shown before Restore and Delete. Shows what will be affected. |
| Progress | Status overlay or inline indicator shown during copy operations. |
| First Run | Empty state on Main when no games configured. Prompts user to add first game. |

# **9\. Acceptance Criteria**

## **Backup**

* Given a configured game, clicking Backup creates a new folder in the backup path with the correct timestamp suffix

* The backup folder contains an exact copy of the source folder

* After backup completes, the backup appears in the list immediately

* Duration and size are displayed

## **Restore**

* Selecting a backup and clicking Restore shows a confirmation dialog

* Cancelling leaves the source folder untouched

* Confirming replaces the source folder with the backup contents

* After restore, the app shows duration and size

## **Delete**

* Selecting a backup and clicking Delete shows a confirmation dialog

* Confirming removes the backup folder from disk

* The backup disappears from the list immediately

## **Configuration**

* The user can add a game by selecting a name, source path, and backup path via file pickers

* The user can delete a game (does not delete backups from disk)

* Configuration persists across app restarts

# **10\. Out of Scope — Future Versions**

* v1.1: Auto-backup on a schedule (configurable interval)

* v1.1: Max backup retention (keep last N, auto-delete older ones)

* v1.2: Backup compression (.zip)

* v2.0: Cloud backup destination (Google Drive, OneDrive)

* v2.0: Game auto-detection from known save paths

