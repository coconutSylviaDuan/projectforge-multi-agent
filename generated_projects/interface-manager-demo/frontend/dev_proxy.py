from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import os


BACKEND = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")


class ProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/"):
            self.proxy()
            return
        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.proxy()
            return
        self.send_error(404, "Not Found")

    def do_PUT(self):
        if self.path.startswith("/api/"):
            self.proxy()
            return
        self.send_error(404, "Not Found")

    def do_PATCH(self):
        if self.path.startswith("/api/"):
            self.proxy()
            return
        self.send_error(404, "Not Found")

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            self.proxy()
            return
        self.send_error(404, "Not Found")

    def proxy(self):
        body = None
        length = self.headers.get("Content-Length")
        if length:
            body = self.rfile.read(int(length))

        headers = {key: value for key, value in self.headers.items() if key.lower() != "host"}
        request = Request(f"{BACKEND}{self.path}", data=body, headers=headers, method=self.command)
        try:
            with urlopen(request, timeout=30) as response:
                payload = response.read()
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in {"transfer-encoding", "connection"}:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(payload)
        except HTTPError as exc:
            payload = exc.read()
            self.send_response(exc.code)
            for key, value in exc.headers.items():
                if key.lower() not in {"transfer-encoding", "connection"}:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(payload)
        except URLError as exc:
            self.send_error(502, f"Backend proxy failed: {exc}")


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    server = ThreadingHTTPServer(("127.0.0.1", 5173), ProxyHandler)
    print("Frontend proxy: http://127.0.0.1:5173 -> " + BACKEND)
    server.serve_forever()
