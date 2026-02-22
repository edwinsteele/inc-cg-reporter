# CLAUDE.md

## What this project does

Generates a monthly Excel report of INC connect group membership from Planning Center Online (PCO) and emails it via SMTP. It's a batch script, not a web service.

## Running

```bash
poetry install
poetry run python -m inc_cg_reporter.app
```

## History

Previously deployed as an AWS Lambda function via the Serverless Framework (`sls`). In Feb 2026 this was removed in favour of running as a plain Python script. Serverless-related files (`serverless.yml`, `package.json`, `node_modules/`, `.serverless/`) are gone.

## Future work

### Remove remaining AWS dependency
- Switch SMTP provider away from AWS SES — any provider (Fastmail, Gmail, Postmark, etc.) works; only `.env` needs changing, no code changes required
- Rotate the SES SMTP credentials in `.env` once a new provider is in place (they date from April 2021)

### GitHub Actions — scheduling
- Add a scheduled workflow (cron: `0 12 1 * *`) that runs `poetry run python -m inc_cg_reporter.app`
- Secrets (`PC_APPLICATION_ID`, `PC_SECRET`, `SMTP_*`, `EMAIL_*`) will need to be added as GitHub Actions secrets

### GitHub Actions — CI (tests & lint)
- Add a workflow that runs on push/PR: `poetry run pytest` and `poetry run mypy`
- Consider adding `poetry run black --check` and `poetry run pylint`

### tox.ini needs an overhaul
- Still references `py38` envlist, `black==20.8b1` (pinned, old), `flake8` (not in dev deps), `pytest-runner` (not needed)
- Either update it to reflect the current toolchain (py310, current black/mypy/pylint) or remove it in favour of the GitHub Actions workflows above

### Other housekeeping
- `pyproject.toml` build-system is old (`poetry>=0.12`, `poetry.masonry.api`) — update to `poetry-core>=1.0.0` / `poetry.core.masonry.api`
- `typing.List` / `typing.Dict` in `excel_writer.py` can be replaced with the built-in `list` / `dict` now that Python 3.10 is the minimum
- Consider adding `inc_cg_reporter/__main__.py` (calling `run()`) so the invocation shortens to `python -m inc_cg_reporter`

## Python

- Runtime: Python 3.10 (via pyenv)
- Package manager: Poetry
- The old py3.8 venv may linger in Poetry's cache (`~/.../virtualenvs/inc-cg-reporter-*-py3.8`); delete it if it causes trouble

## Configuration

All config lives in `.env` (gitignored). Required keys:
- `PC_APPLICATION_ID`, `PC_SECRET` — Planning Center Online API credentials
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` — email relay
- `EMAIL_FROM`, `EMAIL_TO` — sender/recipient
