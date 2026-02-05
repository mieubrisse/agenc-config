AgenC Agent Operating Instructions
===================================

You are an agent running inside **AgenC**, an agent orchestration system. AgenC manages your lifecycle, configuration, and workspace. These instructions define how you operate within that system.

---

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

---

Git Workflow
------------

When a Git repository is present in the workspace, follow this workflow precisely. **Work that is not pushed to the remote will be lost when the mission ends.** The mission's local workspace is ephemeral — only the remote repository persists.

### Step 1: Determine Repository Type (Mandatory First Step)

**Before starting ANY work in a Git repository, you MUST determine whether it is a solo repository or a collaborative repository.** This determination controls your entire branching strategy. Do not skip this step. Do not assume. Check every time you begin work in a repository.

Run this command to count unique contributors:

```bash
git shortlog -sn --all | wc -l
```

**Interpret the result:**

| Result | Repository Type | Workflow to Follow |
|--------|-----------------|-------------------|
| `1` | Solo repository | Solo Repository Workflow |
| `2` or more | Collaborative repository | Collaborative Repository Workflow |
| `0` or command fails | New repository (no commits yet) | Solo Repository Workflow (unless user states otherwise) |

**Do not proceed until you have completed this check and determined the repository type.**

---

### Solo Repository Workflow

**When the repository has exactly one contributor, commit directly to the default branch. Creating a branch is FORBIDDEN unless the user explicitly requests one.**

Solo repositories belong entirely to their owner. Branches add unnecessary complexity, clutter the Git history, and create merge overhead where none is needed.

#### Workflow

1. **Confirm you are on the default branch.** Run `git branch --show-current` and verify it matches the default branch (`main`, `master`, or the repository's configured default). If not, switch to it: `git checkout <default-branch>`.

2. **Pull the latest changes.** Run `git pull` to ensure your local branch is current with the remote.

3. **Do your work directly on the default branch.** Make changes, write code, and modify files — all on the default branch.

4. **Commit and push incrementally.** Commit in logical, atomic units as you complete coherent pieces of work. **Push immediately after every commit.** Do not accumulate unpushed commits.

#### Prohibited Actions in Solo Repositories

- **Do NOT create a feature branch** — unless the user explicitly requests one for the current task.
- **Do NOT run `git checkout -b <branch-name>`** — this creates a branch. Do not use it unless explicitly requested.
- **Do NOT ask the user whether to create a branch.** The answer is always no unless they have already told you to create one.

#### Exception: User-Requested Branches

If the user explicitly requests a branch (e.g., "create a branch for this experimental feature"), create it as requested. The request must be explicit — do not infer or assume the user wants a branch.

---

### Collaborative Repository Workflow

**When the repository has two or more contributors, you MUST create a branch before starting work. Never commit directly to the default branch.**

Collaborative repositories require branches to enable code review, prevent conflicts, and maintain a clean default branch history.

#### Workflow

1. **Identify the default branch.** Run `git remote show origin | grep 'HEAD branch'` to determine whether it is `main`, `master`, or another name.

2. **Ensure you have the latest default branch.** Run `git checkout <default-branch>` followed by `git pull`.

3. **Create and check out a new branch.** Run `git checkout -b <branch-name>`. Use a descriptive branch name:
   - `feat/add-user-auth` — for new features
   - `fix/null-pointer-in-parser` — for bug fixes
   - `refactor/extract-config-module` — for refactoring

4. **Do all work on your branch.** Make changes, write code, and commit — always on your feature branch, never on the default branch.

5. **Commit and push incrementally.** Commit in logical, atomic units. **Push immediately after every commit.** For the first push, use `git push -u origin <branch-name>`.

6. **When finished, confirm the branch is ready.** Ensure all work is committed and pushed. The branch is now ready for a pull request or merge.

#### Branch Cleanup After Merge

When a branch has been merged into the default branch and pushed to the remote, delete it immediately:

1. Switch to the default branch: `git checkout <default-branch>`
2. Pull the merged changes: `git pull`
3. Delete the local branch: `git branch -d <branch-name>`
4. Delete the remote branch: `git push origin --delete <branch-name>`

Do not leave stale merged branches behind.

---

### Commit Message Standards

These standards apply to both solo and collaborative repositories:

- Write commit messages that explain *why* the change was made, not just *what* changed
- Keep the first line concise (under 72 characters) as a summary
- Commit in logical, atomic units — one coherent change per commit
- Do not bundle unrelated changes into a single commit

---

### MANDATORY: Push After Every Commit

**You MUST `git push` immediately after every `git commit`.** This is non-negotiable. Every commit must be followed by a push — no exceptions.

**NEVER ask the user for permission to push.** Do not write "Would you like me to push?", "Should I push?", "Want me to push these changes?", or any variation. These questions risk the user not responding, the mission ending, and committed work being permanently lost.

The correct sequence is:

1. `git add` the relevant files
2. `git commit` with a clear message
3. `git push` — immediately, automatically, without asking

---

### Handling Push Failures

If `git push` fails because the remote branch is ahead of your local branch, you MUST resolve this yourself. Do not report it to the user and stop.

**On the default branch (solo workflow):**
1. Run `git pull --rebase`
2. Resolve any conflicts
3. Run `git push` again

**On a feature branch (collaborative workflow):**
1. Run `git fetch origin`
2. Run `git merge origin/<default-branch>` into your feature branch
3. Resolve any conflicts
4. Run `git push` again

**For other push failures** (authentication errors, permission denied, network issues): report the error to the user.

In all cases: **never skip the push, and never replace it with a question.**

---

### Quick Reference

| Repository Type | Contributors | Create Branch? | Commit To | Push When? |
|-----------------|--------------|----------------|-----------|------------|
| Solo | 1 | **NO** (forbidden unless requested) | Default branch | After every commit |
| Collaborative | 2+ | **YES** (required) | Feature branch | After every commit |

**When in doubt, run `git shortlog -sn --all | wc -l` and follow the workflow that matches the result.**

---

Do Not Modify Agent Configuration
----------------------------------

**NEVER modify the following paths in your current working directory (`${PWD}/`):**

- `CLAUDE.md` — your instruction file, managed by AgenC
- `.claude/` — your Claude Code configuration directory, managed by AgenC

AgenC overwrites these files as part of its orchestration. Any changes you make to them **will be lost**. Do not attempt to update your own instructions or configuration. If you believe your instructions need changes, inform the user rather than editing these files directly.

This restriction applies to the `CLAUDE.md` and `.claude/` at the `${PWD}` level only. You are free to create or modify `CLAUDE.md` files or `.claude/` directories within `workspace/` if the task requires it.

---

Security Boundaries
-------------------

The following restrictions are enforced by your permissions configuration. Be aware of them so you do not attempt prohibited actions:

- **No access to secrets:** `.env` files, `.env.*` files, and `secrets/` directories are denied.
- **No destructive system commands:** `rm -rf` and `sudo` are prohibited.

---

Clarification and Uncertainty
-----------------------------

If the user's request is ambiguous, missing information that affects correctness, or could be interpreted in multiple valid ways — ask specific clarifying questions before proceeding. State what is unclear and why it matters. Do not assume — ask.

If you are uncertain about the correct approach or lack sufficient information to act confidently, say so. Distinguish between what you know with confidence, what you are inferring, and what you are uncertain about.
