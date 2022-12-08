import socket
import threading
FORMAT ="utf-8"

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host=socket.gethostbyname(socket.gethostname())
port=0
s.bind((host, port))
print(s)

ADDR = ('127.0.1.1', 33981)
s.connect(ADDR)
msg="binh".encode(FORMAT)
s.send(msg)
def connv(conn, flag):
  if flag == 1:
    while True:
      msg = input().encode(FORMAT)
      s.send(msg)
  else:
    msg = conn.recv(1024).decode(FORMAT)
    print(msg)

ls = threading.Thread(target=connv, args=(s, 1,))
cs = threading.Thread(target=connv, args=(s, 2,))
ls.start()
cs.start() 
