"""
This module provides a simple HTTP server.
"""

import http.server
import socketserver
import webbrowser
import urllib.parse
from config import GRAPH_CLIENT_ID, EMAIL_PROVIDER

PORT = 8000

# Initialize the authorization_code as an empty string
authorization_code = ""


def get_auth_code():
    """
    Returns the global authorization code.

    This function retrieves the global authorization code and returns it.
    """
    # Return the global authorization_code
    global authorization_code
    return authorization_code


class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    A custom request handler for serving HTTP requests.

    This class extends the SimpleHTTPRequestHandler class
    to provide additional functionality for handling HTTP requests.
    """

    def log_message(self, format, *args):
        """
        Override the log_message method to suppress the HTTP request log.
        """
        pass

    def do_GET(self):
        """
        Handle GET requests.

        This method retrieves the global authorization code.
        """
        global authorization_code

        if self.path.startswith("/?code="):
            query_string = urllib.parse.urlsplit(self.path).query
            params = urllib.parse.parse_qs(query_string)
            authorization_code = params.get("code", [None])[0]
            # print(f"Raw authorization code: {authorization_code}")
            authorization_code = urllib.parse.unquote(authorization_code)
            # print(f"Decoded authorization code: {authorization_code}")

            if authorization_code:
                # print(f"Authorization code: {authorization_code}")
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h1>You can close this window now</h1></body></html>"
                )
                self.wfile.write(b"<script>window.close();</script>")
                self.server.running = False
            else:
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h1>Bad Request.</h1></body></html>")
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Not found.</h1></body></html>")


class StoppableTCPServer(socketserver.TCPServer):
    """
    A TCP server can be stopped by setting the 'running' attribute to False.
    """

    def serve_forever(self):
        self.running = True

        while self.running:
            self.handle_request()


if EMAIL_PROVIDER == "365":
    Handler = MyRequestHandler
    httpd = StoppableTCPServer(("", PORT), Handler)
    # print(f"Serving on port {PORT}")

    # Open the browser automatically
    webbrowser.open(
        f"https://login.microsoftonline.com/bc56a593-6ce0-4fb1-bf21-ea810dbe4170/oauth2/v2.0/authorize?client_id={GRAPH_CLIENT_ID}&response_type=code&redirect_uri=http://localhost:8000/&response_mode=query&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default&state=12345"
    )

    httpd.serve_forever()
    httpd.server_close()
