import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(("127.0.0.1", 8080))

server_socket.listen(5)

print("Server is running on http://127.0.0.1:8080")

client_socket, client_address = server_socket.accept()
print("Connected by:", client_address)

request = client_socket.recv(1024)
print("Request received:")
print(request.decode())

response = "HTTP/1.1 200 OK\r\n"
response += "Content-Type: text/html\r\n"
response += "\r\n"
response += "<html><body><h1>Hello from your server!</h1></body></html>"

client_socket.send(response.encode())

client_socket.close()
server_socket.close()