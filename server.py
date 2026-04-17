import socket
import os
import threading

HOST = "127.0.0.1"
PORT = 8080
WEB_ROOT = "www"


def handle_client(client_socket, client_address):
    print(f"Connected by: {client_address}")

    try:
        request_data = client_socket.recv(1024).decode("utf-8", errors="ignore")
        print("Request received:")
        print(request_data)

        if not request_data:
            return

        lines = request_data.splitlines()
        if not lines:
            return

        request_line = lines[0]
        parts = request_line.split()

        if len(parts) < 3:
            method = ""
            path = "/"
        else:
            method = parts[0]
            path = parts[1]

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
            elif path.endswith(".jpg") or path.endswith(".jpeg"):
                content_type = "image/jpeg"
            elif path.endswith(".png"):
                content_type = "image/png"
            elif path.endswith(".gif"):
                content_type = "image/gif"
            else:
                content_type = "application/octet-stream"

            response_header = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )

            client_socket.sendall(response_header.encode("utf-8"))
            if method != "HEAD":
                client_socket.sendall(body)

        else:
            body = b"<html><body><h1>404 Not Found</h1></body></html>"

            response_header = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            )

            client_socket.sendall(response_header.encode("utf-8"))
            if method != "HEAD":
                client_socket.sendall(body)

    except Exception as e:
        print("Error:", e)

    finally:
        client_socket.close()
        print(f"Connection closed: {client_address}")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Multi-threaded server is running on http://{HOST}:{PORT}")

while True:
    try:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(
            target=handle_client,
            args=(client_socket, client_address)
        )
        client_thread.daemon = True
        client_thread.start()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        break
    except Exception as e:
        print("Server error:", e)

server_socket.close()