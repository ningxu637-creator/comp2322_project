# COMP2322 Multi-threaded Web Server


## Project Overview
This project implements a multi-threaded web server in Python using basic socket programming.  
The server is able to handle HTTP requests from browsers or client programs and return the requested files from the local file system.

Each client connection is handled by a separate thread. The server supports both persistent and non-persistent connections through the `Connection` header field.

---


- Python 3
- Operating System: macOS
- Browser used for testing: Google Chrome
- Command-line tool used for testing: `curl`

---

## how to run
Open a terminal in the project folder and run: python3 server.py
After starting the server, it will listen on: http://127.0.0.1:8080

## Supported Features
The server supports the following functions:

- Multi-threaded web server
- Proper HTTP request and response handling
- GET for text files
- GET for image files
- HEAD request
- Response statuses:
- 200 OK
- 400 Bad Request
- 403 Forbidden
- 404 Not Found
- 304 Not Modified
- Last-Modified response header
- If-Modified-Since request header
- Connection: keep-alive
- Connection: close
- Request logging in server.log

## Project Structure
comp2322_project/
├── server.py
├── README.md
├── server.log
└── www/
    ├── index.html
    ├── hello.txt
    └── image.jpg

## Example Test Commands
Open the home page: curl -i http://127.0.0.1:8080/index.html
Open a text file: curl -i http://127.0.0.1:8080/hello.txt
Open an image file: curl -i http://127.0.0.1:8080/image.jpg
Test HEAD: curl -I http://127.0.0.1:8080/index.html
Test 400 Bad Request: curl -i -X POST http://127.0.0.1:8080/index.html
Test 403 Forbidden: curl --path-as-is -i http://127.0.0.1:8080/../README.md
Test 404 Not Found: curl -i http://127.0.0.1:8080/notfound.html
Test Last-Modified: curl -i http://127.0.0.1:8080/index.html
Test 304 Not Modified(Use the Last-Modified value returned by the previous command): curl -i -H "If-Modified-Since: Fri, 17 Apr 2026 06:50:23 GMT" http://127.0.0.1:8080/index.html
Test Connection: close: curl -i -H "Connection: close" http://127.0.0.1:8080/index.html
Test Connection: keep-alive: curl -i -H "Connection: keep-alive" http://127.0.0.1:8080/index.html

## Log File
The server writes one line to server.log for each request.

Each record includes:
- client IP address
- access time
- requested file name
- response type

Example:
127.0.0.1 - [2026-04-18 11:17:08] "GET /index.html" 200 OK
127.0.0.1 - [2026-04-18 11:17:36] "GET /hello.txt" 200 OK
127.0.0.1 - [2026-04-18 11:17:46] "GET /../README.md" 403 Forbidden
127.0.0.1 - [2026-04-18 11:17:57] "POST /index.html" 400 Bad Request
127.0.0.1 - [2026-04-18 11:18:04] "GET /notfound.html" 404 Not Found

## Notes
The server is implemented using basic socket programming and does not use Python’s built-in HTTPServer class.
The server serves files from the www directory only.
Path traversal attempts containing .. are blocked and return 403 Forbidden.

## GitHub Repository
https://github.com/ningxu637-creator/comp2322_project
