#!/usr/bin/env python3
import argparse
import base64
import mimetypes
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from db import init_db, add_entry, get_db_path, set_default_db_path, set_setting, get_setting

UI_MODES = {'light', 'dark'}


def save_entry(type_, content, *, filename=None, mimetype=None, new_page=False, size=None):
    if new_page:
        add_entry('page_break', '')
    return add_entry(type_, content, filename=filename, mimetype=mimetype, size=size)


def start_viewer():
    server_path = os.path.join(os.path.dirname(__file__), 'server.py')
    os.execv(sys.executable, [sys.executable, server_path])


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
    group.add_argument('--config', metavar='KEY=VALUE', dest='config', help='set a config value (e.g. default_media_size=small)')
    parser.add_argument('text', nargs='?', help='raw text to save')
    parser.add_argument(
        '--new-page',
        '-n',
        action='store_true',
        dest='new_page',
        help='start the new entry on a fresh page',
    )
    parser.add_argument(
        '--size',
        '-s',
        metavar='SIZE',
        dest='size',
        choices=['small', 'medium', 'large'],
        help='media size: small, medium, or large (default: medium)',
    )

    args = parser.parse_args()

    if args.db:
        set_default_db_path(args.db)
        init_db()
        print(f'set db path to {get_db_path()}')
        return

    init_db()

    if args.link:
        entry_id = save_entry('link', args.link, new_page=args.new_page)
        print(f'saved link as entry {entry_id}')

    elif args.code:
        entry_id = save_entry('code', args.code, new_page=args.new_page)
        print(f'saved code snippet as entry {entry_id}')

    elif args.quote:
        entry_id = save_entry('quote', args.quote, new_page=args.new_page)
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
        media_size = None
        if type_ in ('image', 'video'):
            media_size = args.size or get_setting('default_media_size', 'medium')
        entry_id = save_entry(
            type_,
            content,
            filename=filename,
            mimetype=mimetype,
            new_page=args.new_page,
            size=media_size,
        )
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

    elif args.config:
        if '=' not in args.config:
            print(f'error: expected key=value format', file=sys.stderr)
            sys.exit(1)
        key, _, value = args.config.partition('=')
        key = key.strip()
        value = value.strip()
        VALID_CONFIG = {
            'default_media_size': ['small', 'medium', 'large'],
        }
        if key not in VALID_CONFIG:
            print(f'error: unknown config key: {key}', file=sys.stderr)
            print(f'valid keys: {", ".join(VALID_CONFIG)}', file=sys.stderr)
            sys.exit(1)
        if value not in VALID_CONFIG[key]:
            print(f'error: invalid value for {key}: {value} (expected: {", ".join(VALID_CONFIG[key])})', file=sys.stderr)
            sys.exit(1)
        set_setting(key, value)
        print(f'set {key} to {value}')

    elif args.text:
        entry_id = save_entry('text', args.text, new_page=args.new_page)
        print(f'saved text as entry {entry_id}')

    else:
        if sys.stdin.isatty():
            if args.new_page:
                entry_id = add_entry('page_break', '')
                print(f'switched to a new page (entry {entry_id})')
                return
            start_viewer()
        text = sys.stdin.read().strip()
        if not text:
            if args.new_page:
                entry_id = add_entry('page_break', '')
                print(f'switched to a new page (entry {entry_id})')
                return
            start_viewer()
        entry_id = save_entry('text', text, new_page=args.new_page)
        print(f'saved text as entry {entry_id}')


if __name__ == '__main__':
    main()
