
import socket
FORMAT="utf-8"
host=socket.gethostbyname(socket.gethostname())
port=0          # auto port
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.bind((host,port))
print(client)

test_addr=(host,5250)
client.connect(test_addr)           #cant connect 
#print(client)
while True:
    msg=input(">").encode(FORMAT)
    client.send(msg)

