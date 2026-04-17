import socket
import os
import threading

HOST = "127.0.0.1"
PORT = 8080
WEB_ROOT = "www"


def get_content_type(path):
    if path.endswith(".html"):
        return "text/html"
    elif path.endswith(".txt"):
        return "text/plain"
    elif path.endswith(".jpg") or path.endswith(".jpeg"):
        return "image/jpeg"
    elif path.endswith(".png"):
        return "image/png"
    elif path.endswith(".gif"):
        return "image/gif"
    else:
        return "application/octet-stream"


def send_response(client_socket, status_line, content_type, body, method):
    response_header = (
        f"{status_line}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    client_socket.sendall(response_header.encode("utf-8"))
    if method != "HEAD":
        client_socket.sendall(body)


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
            body = b"<html><body><h1>400 Bad Request</h1></body></html>"
            send_response(
                client_socket,
                "HTTP/1.1 400 Bad Request",
                "text/html",
                body,
                "GET"
            )
            return

        method = parts[0]
        path = parts[1]
        version = parts[2]

        print("Method =", method)
        print("Path =", path)
        print("Version =", version)

        if method not in ["GET", "HEAD"]:
            body = b"<html><body><h1>400 Bad Request</h1></body></html>"
            send_response(
                client_socket,
                "HTTP/1.1 400 Bad Request",
                "text/html",
                body,
                method
            )
            return

        if not version.startswith("HTTP/"):
            body = b"<html><body><h1>400 Bad Request</h1></body></html>"
            send_response(
                client_socket,
                "HTTP/1.1 400 Bad Request",
                "text/html",
                body,
                method
            )
            return

        if path == "/":
            path = "/index.html"

        # 403 Forbidden: block path traversal
        if ".." in path:
            body = b"<html><body><h1>403 Forbidden</h1></body></html>"
            send_response(
                client_socket,
                "HTTP/1.1 403 Forbidden",
                "text/html",
                body,
                method
            )
            return

        file_path = os.path.join(WEB_ROOT, path.lstrip("/"))

        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                body = f.read()

            content_type = get_content_type(path)

            send_response(
                client_socket,
                "HTTP/1.1 200 OK",
                content_type,
                body,
                method
            )
        else:
            body = b"<html><body><h1>404 Not Found</h1></body></html>"
            send_response(
                client_socket,
                "HTTP/1.1 404 Not Found",
                "text/html",
                body,
                method
            )

    except Exception as e:
        print("Error:", e)

    finally:
        client_socket.close()
        print(f"Connection closed: {client_address}")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Multi-threaded server is running on http://{HOST}:{PORT}")

    try:
        while True:
            client_socket, client_address = server_socket.accept()

            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()

    except KeyboardInterrupt:
        print("\nServer stopped.")

    finally:
        server_socket.close()


if __name__ == "__main__":
    main()