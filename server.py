import json
import os
import platform
import socket
import sqlite3

# 사용할 IP 및 포트
host = '10.30.122.101'
port = 80

# TCP 소켓 생성
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 이미 할당된 IP라는 오류메세지를 처리하기 위한 코드
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((host, port))

# 서버의 Listen 시작
serverSocket.listen()
print('Now Server listening!...')

# 클라이언트의 접속 확인시
clientSocket, addr = serverSocket.accept()
print(f'Access by {addr}')

# HTTP Method를 식별하고 요청을 처리
request = clientSocket.recv(512).decode().split('\r\n\r\n')
method, uri, version = request[0].split()
payload = request[1]
response = ''

# 지원 가능한 것들 List
ableMethodList = ['GET', 'POST', 'HEAD', 'PUT']
ableVersionList = ['HTTP/1.1']

# 현재 서버에서 구현 또는 제공하는 Method 타입이 아닐 경우
if method not in ableMethodList:
    response = 'HTTP/1.1 405 Method Not Allowed\r\n\r\n<h1>Method Not Allowed</h1>'

# 현재 서버에서 지원하는 HTTP 프로토콜의 version이 아닐 경우
if version not in ableVersionList:
    response = 'HTTP/1.1 505 Version Not Supported\r\n\r\n<h1>HTTP Version Not Supported</h1>'

else:
    # GET 요청을 처리
    if method == 'GET':
        absPath = os.getcwd()

        # 파일을 가져오는데 존재하는지 확인
        try:
            file = open(absPath + uri, 'r')
            body = file.read()
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(body)}\r\nServer: {platform.platform()}\r\n\r\n' + body
        except FileNotFoundError as e:
            response = f'HTTP/1.1 404 Not Found\r\nServer: {platform.platform()}\r\n\r\nPage doesn\'t exist!!!'

    # POST 요청을 처리
    if method == 'POST':
        # 유저 데이터를 관리용 DB생성
        conn = sqlite3.connect(uri.split('/')[-1])
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS user_table(id PRIMARY KEY, pwd)")

        # json 형태의 페이로드를 python built-in dictionary로 parsing 후 DB에 등록
        info = json.loads(payload)
        cursor.execute("INSERT INTO user_table VALUES(?, ?);", (info['id'], info['pwd']))

        # 현재 User 테이블에 등록된 사용자를 확인한다.
        cursor.execute('SELECT * FROM user_table')
        for row in cursor.fetchall():
            print(row)

        response = f'HTTP/1.1 200 OK\r\nServer: {platform.platform()}'
        # DB에 변경사항을 반영하고 닫는다.
        cursor.close()
        conn.commit()
        conn.close()

    # HEAD 요청을 처리
    if method == 'HEAD':
        absPath = os.getcwd()
        filePath = absPath + uri
        if os.path.exists(filePath):
            response = f'HTTP/1.1 200 OK\r\nServer: {platform.platform()}'
        else:
            response = f'HTTP/1.1 404 Not Found\r\nServer: {platform.platform()}'

    # PUT 요청을 처리
    if method == 'PUT':
        currPath = os.getcwd()
        pathComponent = uri.split('/')

        # 요청받은 request의 URI에 담긴 경로를 추적해 나가며 파일을 생성한다.
        for i in range(len(pathComponent)):
            entity = pathComponent[i]
            if i == len(pathComponent) - 1:
                # 요청한 파일이 있을 경우
                if os.path.exists(currPath + entity):
                    file = open(currPath + entity, 'w')
                    file.write(payload)
                    response = f'HTTP/1.1 200 OK\r\nContent-Location: {currPath + entity}\r\n'

                # 요청한 파일이 없을 경우
                else:
                    file = open(currPath + entity, 'w')
                    file.write(payload)
                    response = f'HTTP/1.1 201 Created\r\nContent-Location: {currPath + entity}'

            # 요청한 경로에 디렉토리가 존재하지 않을 경우
            elif not os.path.exists(currPath + '/' + entity):
                os.makedirs(currPath + entity)
                currPath += entity + '/'

            # 요청한 경로에 디렉토리가 존재할 경우
            else:
                currPath += entity + '/'

clientSocket.send(response.encode())
clientSocket.close()