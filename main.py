from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mimetypes
import pathlib
import socket
import threading
import urllib.parse
import os
from datetime import datetime


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.pr_url = urllib.parse.urlparse(self.path)
        file_path = os.path.join(os.path.dirname(__file__), self.pr_url.path[1:])
        if os.path.exists(file_path):
            if self.pr_url.path == '/':
                self.send_html_file('index.html')
            elif self.pr_url.path == '/message':
                self.send_html_file('message.html')
            else:
                self.send_static()
        else:
            self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        file_path = os.path.join(os.path.dirname(__file__), filename)
        with open(file_path, 'rb') as fd:
            self.wfile.write(fd.read())
            
    def send_static(self):
        self.send_response(200)
        file_name = os.path.basename(self.path)
        mt = mimetypes.guess_type(file_name)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        file_path = os.path.join(os.path.dirname(__file__), self.pr_url.path[1:])
        with open(file_path, 'rb') as file:
            self.wfile.write(file.read())
            
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        post_params = urllib.parse.parse_qs(data.decode())

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
        socket_client.send_data(post_params)


class SocketClient:
    def __init__(self):
        self.data_file = os.path.join(
            os.path.dirname(__file__), 'storage', 'data.json')

    def send_data(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(json.dumps(data).encode(), ('localhost', 5000))

    def save_data(self, data):
        data_dict = json.loads(data)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        new_data = {
            current_time: data_dict
        }

        existing_data = {}
        if os.path.exists(self.data_file) and os.stat(self.data_file).st_size > 0:
            with open(self.data_file, 'r') as file:
                existing_data = json.load(file)

        existing_data.update(new_data)

        with open(self.data_file, 'w') as file:
            json.dump(existing_data, file)


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 8000)
    http_server = server_class(server_address, handler_class)
    http_server.serve_forever()


def run_socket_server(socket_client):
    server_address = ('', 5000)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(server_address)
        while True:
            data, _ = sock.recvfrom(1024)
            socket_client.save_data(data.decode())


if __name__ == '__main__':
    import threading

    socket_client = SocketClient()

    http_thread = threading.Thread(target=run_http_server)
    socket_thread = threading.Thread(
        target=run_socket_server, args=(socket_client,))

    http_thread.start()
    socket_thread.start()

    http_thread.join()
    socket_thread.join()
