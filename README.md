# UFC Downloader

CLI utilities to index UFC events and import UFC downloads into a Plex-friendly directory layout.

## Commands

```bash
# Update cached event index from TheSportsDB
ufc_downloader index-events

# Match downloaded UFC folders against the index and import into the destination library
ufc_downloader import-downloads
```

## Current Behavior

- `index-events`:
  - Fetches UFC events for the current year from TheSportsDB.
  - Writes `events_<year>.json` in the current working directory.
  - Skips refresh unless `--force` or cache is older than `--freshness_days`.

- `import-downloads`:
  - Scans `SOURCE_DIR` (`/volume1/data/sabnzbd/completed/`) for folders with prefix `UFC.`.
  - Fuzzy-matches source titles to indexed events.
  - Imports matched content to `DEST_DIR` (`/volume1/data/media/movies`) with edition tags.

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install . pytest
python -m pytest -q
```

## Container

Build:

```bash
docker build -t ghcr.io/austinkeller/ufc-downloader:dev .
```

Run:

```bash
docker run --rm \
  -v /volume1/data:/volume1/data \
  ghcr.io/austinkeller/ufc-downloader:dev index-events --force
```

## GitHub Actions / GHCR

Workflow: `.github/workflows/publish-image.yml`

- Runs tests on push + PR.
- Publishes image to `ghcr.io/austinkeller/ufc-downloader` on:
  - push to `main`
  - tag push (`v*`)
  - manual dispatch

