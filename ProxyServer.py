import socket
import ssl
from threading import Thread
from urllib.parse import urlencode


class ProxyServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.buffer_size = 4096

    def handle_client(self, client_socket):
        request = client_socket.recv(self.buffer_size)
        if request:
            first_line = request.split(b'\n')[0]
            method = first_line.split(b' ')[0]
            url = first_line.split(b' ')[1]
            dest_host = url.split(b"://")[1].split(b"/")[0]
            dest_port = 80

            if b'https://' in url:
                dest_port = 443

            params = {}
            if method == b'POST':
                headers = request.split(b'\r\n\r\n', 1)[0]
                body = request.split(b'\r\n\r\n', 1)[1]
                params = body.decode()

            dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dest_socket.connect((dest_host, dest_port))
            if dest_port == 443:
                dest_socket = ssl.wrap_socket(dest_socket, ssl_version=ssl.PROTOCOL_SSLv23)

            if method == b'GET':
                dest_socket.sendall(request)
            elif method == b'POST':
                dest_socket.sendall(request.split(b'\r\n\r\n', 1)[0] + b'\r\n\r\n' + urlencode(params).encode())

            while True:
                response = dest_socket.recv(self.buffer_size)
                if len(response) > 0:
                    client_socket.send(response)
                else:
                    break

            dest_socket.close()
            client_socket.close()

    def start(self):
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_socket.bind((self.host, self.port))
        proxy_socket.listen(5)
        print(f"Proxy server listening on {self.host}:{self.port}")

        while True:
            client_socket, addr = proxy_socket.accept()
            print(f"Accepted connection from {addr[0]}:{addr[1]}")
            client_handler = Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()


if __name__ == "__main__":
    proxy = ProxyServer('127.0.0.1', 8888)
    proxy.start()

