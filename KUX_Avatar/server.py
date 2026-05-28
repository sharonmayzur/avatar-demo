#!/usr/bin/env python3
import http.server, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
ROOT = os.path.dirname(os.path.abspath(__file__))

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)
    def do_GET(self):
        path = os.path.join(ROOT, self.path.lstrip('/').split('?')[0])
        if os.path.isfile(path):
            super().do_GET()
        else:
            self.path = '/index.html'
            super().do_GET()
    def log_message(self, fmt, *args):
        print(f"  {fmt % args}")

with http.server.HTTPServer(('', PORT), SPAHandler) as s:
    print(f"Running at http://localhost:{PORT}/page/homepage")
    s.serve_forever()
