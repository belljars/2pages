#!/usr/bin/env python3
import http.server
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from db import init_db, get_entries, get_count, get_setting

UI_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'ui'))
PORT = 7267

MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css':  'text/css',
    '.js':   'application/javascript',
}

# static files loaded once at startup: path -> (mime, bytes)
_static: dict = {}

def _load_static():
    for name in os.listdir(UI_DIR):
        path = os.path.join(UI_DIR, name)
        if os.path.isfile(path):
            ext  = os.path.splitext(name)[1].lower()
            mime = MIME_TYPES.get(ext, 'application/octet-stream')
            with open(path, 'rb') as f:
                _static['/' + name] = (mime, f.read())
    if '/index.html' in _static:
        _static['/'] = _static['/index.html']


class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # silence default request logging

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == '/api/entries':
            self.send_json({'entries': get_entries()})
            return

        if path == '/api/count':
            self.send_json({'count': get_count()})
            return

        if path == '/api/settings':
            self.send_json({'ui_mode': get_setting('ui_mode', 'light')})
            return

        # static files served from memory
        entry = _static.get(path)
        if entry:
            mime, body = entry
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()


def main():
    init_db()
    _load_static()
    server = http.server.ThreadingHTTPServer(('localhost', PORT), Handler)
    print(f'2pages  →  http://localhost:{PORT}')
    server.serve_forever()


if __name__ == '__main__':
    main()
