#!/usr/bin/env python3
import argparse
import base64
import mimetypes
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from db import init_db, add_entry


def main():
    parser = argparse.ArgumentParser(
        description='Add an entry to your 2pages archive.',
        epilog='With no flags, pass text as a positional arg or pipe it via stdin.',
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--link', metavar='URL', help='save a URL')
    group.add_argument('--code', metavar='SNIPPET', help='save a code snippet')
    group.add_argument('--quote', metavar='TEXT', help='save text as a quote')
    group.add_argument('--file', metavar='PATH', help='save a file (image, video, or other)')
    parser.add_argument('text', nargs='?', help='raw text to save')

    args = parser.parse_args()
    init_db()

    if args.link:
        entry_id = add_entry('link', args.link)
        print(f'saved link as entry {entry_id}')

    elif args.code:
        entry_id = add_entry('code', args.code)
        print(f'saved code snippet as entry {entry_id}')

    elif args.quote:
        entry_id = add_entry('quote', args.quote)
        print(f'saved quote as entry {entry_id}')

    elif args.file:
        path = args.file
        if not os.path.isfile(path):
            print(f'error: file not found: {path}', file=sys.stderr)
            sys.exit(1)
        mimetype, _ = mimetypes.guess_type(path)
        if mimetype and mimetype.startswith('image/'):
            type_ = 'image'
        elif mimetype and mimetype.startswith('video/'):
            type_ = 'video'
        else:
            type_ = 'file'
        with open(path, 'rb') as f:
            data = base64.b64encode(f.read()).decode()
        mime_str = mimetype or 'application/octet-stream'
        content = f'data:{mime_str};base64,{data}'
        filename = os.path.basename(path)
        entry_id = add_entry(type_, content, filename=filename, mimetype=mimetype)
        print(f'saved {type_} "{filename}" as entry {entry_id}')

    elif args.text:
        entry_id = add_entry('text', args.text)
        print(f'saved text as entry {entry_id}')

    else:
        if sys.stdin.isatty():
            parser.print_help()
            sys.exit(1)
        text = sys.stdin.read().strip()
        if not text:
            parser.print_help()
            sys.exit(1)
        entry_id = add_entry('text', text)
        print(f'saved text as entry {entry_id}')


if __name__ == '__main__':
    main()
