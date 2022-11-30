import socket 

IP = socket.gethostbyname(socket.gethostname())
PORT = 4500 
ADDR = (IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = ":disconnect"
SIZE = 1024

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

msg = DISCONNECT_MSG.encode(FORMAT)
client.send(msg)