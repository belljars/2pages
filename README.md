# 2pages

A small local archive for short text, links, code snippets, and files. Learn to be content with the natural mess of a scrapbook.w

## Setup

```bash
./script/setup.sh
```

This initializes the database and installs the `2p` command to `~/.local/bin/2p`.

## Usage

Start the viewer:

```bash
2p
```

Open `http://localhost:7267`.

Add content:

```bash
2p "some text"
2p --link https://example.com
2p --q "A short quote"
2p --c 'print("hello")'
2p --f path/to/file
2p --e
2p --ui dark
echo "text from stdin" | 2p
```
