import functools
import http.server

import sys
import threading
import time

import nox


def start_server():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory="_site")
    server = http.server.HTTPServer(("127.0.0.1", 4000), handler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("Serving at http://127.0.0.1:4000/")
    return server_thread


@nox.session
def build(session):
    # session.install("-r", "requirements.txt")

    if sys.stderr.isatty():
        session.run("python", "serve.py")
    else:
        session.run("python", "blog.py")
