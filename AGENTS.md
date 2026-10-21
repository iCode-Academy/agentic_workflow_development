# Development rules for agents

## Project
- School management app. Django 5.2, Python 3.12, SQLite (db.sqlite3, dev only).
- Setup: uv sync && source .venv/bin/activate (uv manages Python, the venv and packages; never use pip).
- Run tests: pytest
- Run app: python manage.py runserver
- Lint: ruff check .
- One Django app per domain: students, teachers, courses, attendance.
- After model changes: python manage.py makemigrations && python manage.py migrate. Commit migration files.

## Before coding
- Read the relevant models, views, urls, templates and tests first.
- Propose a plan and wait for approval before editing files.
- Work only on the current branch. Never switch to or commit on `main`.

## While coding
- Smallest complete change. No unrelated refactoring.
- Follow existing naming and file layout.
- Add or update tests for every behaviour change.
- Do not add dependencies without asking. Never run `uv add` or `uv remove` without approval.

## Before finishing
- Run pytest and ruff check .
- Show `git diff --stat` and summarise what changed and what is unverified.

## Never
- Read or print `.env`, `auth.json`, or any API key.
- Delete db.sqlite3 or existing migration files.
- Run `git push --force`, `git reset --hard`, `rm -rf`, or `migrate <app> zero`.
