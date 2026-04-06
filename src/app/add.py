#!/usr/bin/env python3
import argparse
import base64
import mimetypes
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from db import init_db, add_entry, get_db_path, set_default_db_path, set_setting

UI_MODES = {'light', 'dark'}


def main():
    parser = argparse.ArgumentParser(
        description='Add an entry to your 2pages archive.',
        epilog='With no flags, pass text as a positional arg or pipe it via stdin.',
        color=False,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--link', '--l', metavar='URL', dest='link', help='save a URL')
    group.add_argument('--code', '--c', metavar='SNIPPET', dest='code', help='save a code snippet')
    group.add_argument('--quote', '--q', metavar='TEXT', dest='quote', help='save text as a quote')
    group.add_argument('--file', '--f', metavar='PATH', dest='file', help='save a file (image, video, or other)')
    group.add_argument('--empty-page', '--e', action='store_true', dest='empty_page', help='insert an intentional empty page')
    group.add_argument('--db', metavar='PATH', dest='db', help='set the default archive.db path')
    group.add_argument('--ui', metavar='MODE', dest='ui', help='set viewer theme: light or dark')
    parser.add_argument('text', nargs='?', help='raw text to save')

    args = parser.parse_args()

    if args.db:
        set_default_db_path(args.db)
        init_db()
        print(f'set db path to {get_db_path()}')
        return

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

    elif args.empty_page:
        entry_id = add_entry('empty_page', '')
        print(f'saved intentional empty page as entry {entry_id}')

    elif args.ui:
        mode = args.ui.lower()
        if mode not in UI_MODES:
            print(f"error: invalid ui mode: {args.ui} (expected: light or dark)", file=sys.stderr)
            sys.exit(1)
        set_setting('ui_mode', mode)
        print(f'set ui mode to {mode}')

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
