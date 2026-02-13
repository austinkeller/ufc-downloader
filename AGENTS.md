# Agent Notes (ufc-downloader)

Keep this file short and action-oriented.

## Scope

This repo owns the `ufc_downloader` CLI and its container image used by scheduled jobs.

## Tooling

- Python 3.9+ expected.
- Prefer stdlib + existing lightweight deps (`click`, `requests`).

## Git Hygiene

- Commit early and often; prefer small, focused commits.
- Sanity checks before commit:
  - `git status -sb`
  - `git diff`
  - `python -m pytest -q`

## Container/Release

- Keep image deterministic and small.
- GHCR publish is handled by `.github/workflows/publish-image.yml`.

## Secrets

- Do not commit secrets.
- Runtime config should be env vars + mounted volumes only.
