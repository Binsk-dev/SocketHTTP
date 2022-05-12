import socket

serverIp = '10.30.122.101'
port = 80

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 소켓 생성까지
clientSocket.connect((serverIp, port))

# 메세지 전송
#request = 'GET /pages/index.html HTTP/1.1\r\n\r\n'
request = 'GET /pages/indx.html HTTP/1.1\r\n\r\n'
#request = 'PUT /pages/new.html HTTP/1.1\r\n\r\n<h1>This is new file!</h1>'
#request = 'HEAD /pages/index.html HTTP/1.1\r\n\r\n'
#request = 'HEAD /pages/index.html HTTP/1.2\r\n\r\n'
#request = 'DELETE /pages/index.html HTTP/1.1\r\n\r\n'
#request = 'POST /user.db HTTP/1.1\r\nContent-Type: application/json\r\n\r\n'
#body = '{"id": 20181690, "pwd": "lyj1234"}'
#request += body
clientSocket.send(request.encode())

# 메세지 수신
response = clientSocket.recv(512)
print(response.decode())

# 통신 종료
clientSocket.close()
