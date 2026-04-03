# 2pages

Minimal personal archive. Save text, links, code snippets, images, videos, and other files from the terminal, then browse them in a local two-page viewer.

## What It Does

- Stores entries in a local SQLite database at `archive.db`
- Starts a local viewer at `http://localhost:7267`
- Shows text, code, links, files, images, and videos
- Renders images and videos as full-spread pages

This project is plain Python, HTML, CSS, and JavaScript. There is no Node setup or package manager step.

## Setup

```bash
bash script/setup.sh
```

This does two things:

- Initializes `archive.db`
- Installs the `log` command as `~/.local/bin/log`

If `~/.local/bin` is not on your `PATH`, add it in your shell config:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Usage

```bash
log                          # start the viewer at http://localhost:7267
log --serve                  # same as above
log "some text"              # save raw text
log --link https://…         # save a URL
log --code "snippet"         # save a code snippet
log --file path/to/file      # save an image, video, or other file
echo "text" | log            # save text from stdin
```

With no arguments, `log` starts the local server. With arguments, it adds an entry to the archive.

## Notes

- Page numbers correspond to entry IDs in the database
- Navigation starts at page `1`
- Text, code, link, and generic file entries can share a spread
- Image and video entries take the full spread by themselves
