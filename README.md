# 2pages

Minimal personal archive. Save links, text, code snippets, images, and files from the terminal — browse them as a two-page spread in the browser.

## setup

```bash
bash script/setup.sh
```

Initializes the database and installs the `log` command to `~/.local/bin`. Add `~/.local/bin` to your `$PATH` if it isn't already.

## usage

```bash
log                          # start the viewer at http://localhost:7267
log "some text"              # save raw text
log --link https://…         # save a URL
log --code "snippet"         # save a code snippet
log --file path/to/file      # save an image, video, or other file
echo "text" | log            # save from stdin
```

Page 1 is the oldest entry. The highest page number is the most recent.
