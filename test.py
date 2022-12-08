import socket
FORMAT ="utf-8"

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host=socket.gethostbyname(socket.gethostname())
port=0
s.bind(('127.0.1.1', port))
print(s)

ADDR = ('127.0.1.1', 43701)
s.connect(ADDR)

msg="hello".encode(FORMAT)
s.send(msg)