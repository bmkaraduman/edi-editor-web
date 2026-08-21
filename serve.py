#!/usr/bin/env python3
"""EDI Editor Web - basit statik geliştirme sunucusu.

Kullanim:  python3 serve.py [port]      (varsayilan: 5599)
Ardindan tarayicida: http://localhost:5599
"""
import os
import sys
import functools
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5599


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    os.chdir(ROOT)
    handler = functools.partial(Handler, directory=ROOT)
    print("EDI Editor Web -> http://localhost:%d" % PORT, flush=True)
    HTTPServer(("127.0.0.1", PORT), handler).serve_forever()
