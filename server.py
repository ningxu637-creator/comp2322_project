import socket
import os
import threading
from datetime import datetime
from email.utils import formatdate, parsedate_to_datetime

HOST = "127.0.0.1"
PORT = 8080
WEB_ROOT = "www"
LOG_FILE = "server.log"


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


def get_last_modified_header(file_path):
    mtime = os.path.getmtime(file_path)
    return formatdate(mtime, usegmt=True)


def write_log(client_address, method, path, status_text):
    access_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_ip = client_address[0]
    log_line = f'{client_ip} - [{access_time}] "{method} {path}" {status_text}\n'

    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(log_line)


def send_response(client_socket, status_line, content_type, body, method,
                  connection_value="close", extra_headers=""):
    response_header = (
        f"{status_line}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: {connection_value}\r\n"
        f"{extra_headers}"
        "\r\n"
    )

    client_socket.sendall(response_header.encode("utf-8"))
    if method != "HEAD" and not status_line.startswith("HTTP/1.1 304"):
        client_socket.sendall(body)


def parse_headers(lines):
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
    return headers


def process_request(client_socket, client_address, request_data):
    method = "UNKNOWN"
    path = "/"
    status_text = "500 Internal Server Error"

    lines = request_data.splitlines()
    if not lines:
        return "close"

    request_line = lines[0]
    parts = request_line.split()

    headers = parse_headers(lines)
    connection_value = headers.get("connection", "close").lower()

    if connection_value not in ["keep-alive", "close"]:
        connection_value = "close"

    if len(parts) < 3:
        body = b"<html><body><h1>400 Bad Request</h1></body></html>"
        status_text = "400 Bad Request"
        send_response(
            client_socket,
            "HTTP/1.1 400 Bad Request",
            "text/html",
            body,
            "GET",
            connection_value
        )
        write_log(client_address, method, path, status_text)
        return connection_value

    method = parts[0]
    path = parts[1]
    version = parts[2]

    print("Method =", method)
    print("Path =", path)
    print("Version =", version)
    print("Connection =", connection_value)

    if method not in ["GET", "HEAD"]:
        body = b"<html><body><h1>400 Bad Request</h1></body></html>"
        status_text = "400 Bad Request"
        send_response(
            client_socket,
            "HTTP/1.1 400 Bad Request",
            "text/html",
            body,
            method,
            connection_value
        )
        write_log(client_address, method, path, status_text)
        return connection_value

    if not version.startswith("HTTP/"):
        body = b"<html><body><h1>400 Bad Request</h1></body></html>"
        status_text = "400 Bad Request"
        send_response(
            client_socket,
            "HTTP/1.1 400 Bad Request",
            "text/html",
            body,
            method,
            connection_value
        )
        write_log(client_address, method, path, status_text)
        return connection_value

    if path == "/":
        path = "/index.html"

    if ".." in path:
        body = b"<html><body><h1>403 Forbidden</h1></body></html>"
        status_text = "403 Forbidden"
        send_response(
            client_socket,
            "HTTP/1.1 403 Forbidden",
            "text/html",
            body,
            method,
            connection_value
        )
        write_log(client_address, method, path, status_text)
        return connection_value

    file_path = os.path.join(WEB_ROOT, path.lstrip("/"))

    if os.path.exists(file_path):
        last_modified = get_last_modified_header(file_path)
        extra_headers = f"Last-Modified: {last_modified}\r\n"

        if "if-modified-since" in headers:
            try:
                ims_time = int(parsedate_to_datetime(headers["if-modified-since"]).timestamp())
                file_mtime = int(os.path.getmtime(file_path))

                if file_mtime <= ims_time:
                    status_text = "304 Not Modified"
                    send_response(
                        client_socket,
                        "HTTP/1.1 304 Not Modified",
                        get_content_type(path),
                        b"",
                        method,
                        connection_value,
                        extra_headers
                    )
                    write_log(client_address, method, path, status_text)
                    return connection_value
            except Exception:
                pass

        with open(file_path, "rb") as f:
            body = f.read()

        content_type = get_content_type(path)
        status_text = "200 OK"

        send_response(
            client_socket,
            "HTTP/1.1 200 OK",
            content_type,
            body,
            method,
            connection_value,
            extra_headers
        )
        write_log(client_address, method, path, status_text)
    else:
        body = b"<html><body><h1>404 Not Found</h1></body></html>"
        status_text = "404 Not Found"
        send_response(
            client_socket,
            "HTTP/1.1 404 Not Found",
            "text/html",
            body,
            method,
            connection_value
        )
        write_log(client_address, method, path, status_text)

    return connection_value


def handle_client(client_socket, client_address):
    print(f"Connected by: {client_address}")
    client_socket.settimeout(10)

    try:
        while True:
            request_data = client_socket.recv(4096).decode("utf-8", errors="ignore")
            if not request_data:
                break

            print("Request received:")
            print(request_data)

            connection_value = process_request(client_socket, client_address, request_data)

            if connection_value == "close":
                break

    except socket.timeout:
        print(f"Connection timeout: {client_address}")
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