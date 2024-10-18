import http.server
import socketserver
import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Define the request handler
class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        log.info(f"Received GET request for: {self.path}")
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        # Example response
        response = {
            "message": "Hello, world!",
            "path": self.path
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        log.info(f"Received POST request for: {self.path}")
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        log.debug(f"POST data: {post_data}")
        
        # You can process the POST data here
        response = {
            "received": post_data.decode('utf-8')
        }
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

# Set up the server
PORT = 8085
handler = MyRequestHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    log.info(f"Serving on port {PORT}")
    httpd.serve_forever()