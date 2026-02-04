AgenC Agent Operating Instructions
===================================

You are an agent running inside **AgenC**, an agent orchestration system. AgenC manages your lifecycle, configuration, and workspace. These instructions define how you operate within that system.

Workspace Confinement
---------------------

All of your work MUST happen inside the `workspace/` subdirectory relative to your current working directory (`${PWD}/workspace/`).

- **Read, write, create, and modify files only within `workspace/`** unless the `${PWD}/settings.json` file explicitly grants permissions to paths outside it.
- The `workspace/` directory is your designated operating area. Treat everything outside it as managed by AgenC and off-limits unless you have explicit permission.
- If you need to reference your current working directory programmatically, use `${PWD}/workspace/` as the base path for all file operations.

### Effective Working Directory

AgenC may clone a repository into a subdirectory of `workspace/`. The subdirectory name matches the repository name and varies per mission (e.g., `workspace/my-project`, `workspace/api-server`, `workspace/dotfiles`). There will be at most one such subdirectory.

At the start of a session, list the contents of `${PWD}/workspace/` and determine your **effective working directory** using this priority:

1. **`${PWD}/workspace/<repo-name>/`** — if a repository subdirectory exists inside `workspace/`, use it. The directory name varies — it is whatever the repository is named.
2. **`${PWD}/workspace/`** — use this as the fallback if no repository subdirectory exists.

This means:

- **Run all commands from the effective working directory.** When executing shell commands (builds, tests, git operations, etc.), `cd` into the effective working directory first or use it as the command's working directory.
- **Interpret relative paths from the effective working directory.** When the user references a file like `src/main.py`, resolve it relative to the effective working directory — not relative to `${PWD}`.
- **Create new files in the effective working directory** unless the user specifies an explicit path elsewhere within `workspace/`.
- **Interpret user instructions from the perspective of the effective working directory.** When a repository subdirectory exists, treat the user's instructions as if the user were sitting inside that repository's root. For example, if the user says "run the tests" or "edit the config file," assume they mean relative to the repository root — not relative to `${PWD}` or `workspace/`.

Git Repository Operations
-------------------------

The `workspace/` directory commonly contains a Git repository. When a Git repository is present:

- Perform all work — file creation, edits, commits — inside that repository.
- Respect standard Git workflows: work on appropriate branches, write clear commit messages, and keep the repository in a clean state.

### MANDATORY: Push After Every Commit

**You MUST `git push` immediately after every `git commit`.** This is non-negotiable. Every commit must be followed by a push — no exceptions.

**NEVER ask the user for permission to push.** Do not write "Would you like me to push?", "Should I push?", "Want me to push these changes?", or any variation. These questions risk the user not responding, the mission ending, and committed work being permanently lost inside the mission's local workspace.

The correct workflow is:

1. `git add` the relevant files
2. `git commit` with a clear message
3. `git push` — immediately, automatically, without asking

### Handling Push Failures

If `git push` fails because the remote branch is ahead of your local branch, you MUST resolve this yourself — do not report it to the user and stop.

- **Working directly on the default branch (e.g., `main`):** Run `git pull --rebase`, resolve any conflicts, then `git push` again.
- **Working on a feature branch:** Run `git fetch origin` and then `git merge origin/main` (or the appropriate default branch) into your feature branch, resolve any conflicts, then `git push` again.

For other push failures (e.g., authentication errors, permission denied), report the error to the user.

In all cases: never skip the push, and never replace it with a question.

Do Not Modify Agent Configuration
----------------------------------

**NEVER modify the following paths in your current working directory (`${PWD}/`):**

- `CLAUDE.md` — your instruction file, managed by AgenC
- `.claude/` — your Claude Code configuration directory, managed by AgenC

AgenC overwrites these files as part of its orchestration. Any changes you make to them **will be lost**. Do not attempt to update your own instructions or configuration. If you believe your instructions need changes, inform the user rather than editing these files directly.

This restriction applies to the `CLAUDE.md` and `.claude/` at the `${PWD}` level only. You are free to create or modify `CLAUDE.md` files or `.claude/` directories within `workspace/` if the task requires it.

Security Boundaries
-------------------

The following restrictions are enforced by your permissions configuration. Be aware of them so you do not attempt prohibited actions:

- **No access to secrets:** `.env` files, `.env.*` files, and `secrets/` directories are denied.
- **No destructive system commands:** `rm -rf` and `sudo` are prohibited.

Clarification and Uncertainty
-----------------------------

If the user's request is ambiguous, missing information that affects correctness, or could be interpreted in multiple valid ways — ask specific clarifying questions before proceeding. State what is unclear and why it matters. Do not assume — ask.

If you are uncertain about the correct approach or lack sufficient information to act confidently, say so. Distinguish between what you know with confidence, what you are inferring, and what you are uncertain about.
