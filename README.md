# 2pages

Small local archive for saving short text, links, code snippets, and files, then browsing them in a simple two-page viewer.

## What It Does

- Stores entries in a local SQLite database (`archive.db`)
- Serves a small browser UI at `http://localhost:7267`
- Includes a `2p` helper command for adding entries or starting the viewer

## Repo Layout

- `src/app/` Python backend and database code
- `src/ui/` Static frontend files
- `script/2p` Main helper script
- `script/setup.sh` Optional setup script

## Quick Start

Run the setup script once:

```bash
./script/setup.sh
```

Or use the helper script directly:

```bash
./script/2p
```

Then open `http://localhost:7267`.

## Test Script

Run the fixture-based test runner:

```bash
./script/test
```

It loads files from `test/`, writes into a temporary SQLite database, and verifies that text, code, image, video, and generic file imports are stored correctly.

To load the same fixture data into the real app database so it appears in the UI:

```bash
./script/load-test-data
```

That command writes directly into `archive.db`, unlike `./script/test`, which uses a temporary database and deletes it after verification.

## Adding Entries

```bash
./script/2p "your text here"
./script/2p --link https://example.com
./script/2p --quote "quoted text"
./script/2p --code 'print("hello")'
./script/2p --file path/to/file.png
echo "piped text" | ./script/2p
```

## Notes

- The database file is created at the repo root as `archive.db`
- `script/setup.sh` installs `script/2p` as `~/.local/bin/2p`
- The app uses Python standard library modules plus SQLite, so no dependency install step is currently required
