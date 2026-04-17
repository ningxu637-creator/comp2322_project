import socket
import os

HOST = "127.0.0.1"
PORT = 8080
WEB_ROOT = "www"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Server is running on http://{HOST}:{PORT}")

client_socket, client_address = server_socket.accept()
print("Connected by:", client_address)

request = client_socket.recv(1024).decode()
print("Request received:")
print(request)

request_line = request.splitlines()[0]
parts = request_line.split()

if len(parts) >= 2:
    method = parts[0]
    path = parts[1]
else:
    method = ""
    path = "/"

if path == "/":
    path = "/index.html"

file_path = os.path.join(WEB_ROOT, path.lstrip("/"))

if os.path.exists(file_path):
    with open(file_path, "rb") as f:
        body = f.read()

    if path.endswith(".html"):
        content_type = "text/html"
    elif path.endswith(".txt"):
        content_type = "text/plain"
    else:
        content_type = "application/octet-stream"

    response_header = "HTTP/1.1 200 OK\r\n"
    response_header += f"Content-Type: {content_type}\r\n"
    response_header += f"Content-Length: {len(body)}\r\n"
    response_header += "\r\n"

    client_socket.send(response_header.encode() + body)
else:
    body = b"<html><body><h1>404 Not Found</h1></body></html>"

    response_header = "HTTP/1.1 404 Not Found\r\n"
    response_header += "Content-Type: text/html\r\n"
    response_header += f"Content-Length: {len(body)}\r\n"
    response_header += "\r\n"

    client_socket.send(response_header.encode() + body)

client_socket.close()
server_socket.close()