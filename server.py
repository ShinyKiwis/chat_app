# Main server 

import socket 
import threading
from database import *

IP = socket.gethostbyname(socket.gethostname())
PORT = 4500 
ADDR = (IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = ":disconnect"
SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(ADDR)
s.listen(5)

connection_list = []


def on_new_client(client_socket, addr):
  print(f"[NEW CONNECTION]: {addr} connected")
  connected = True
  while connected:
    msg = client_socket.recv(SIZE).decode(FORMAT)
    print(f"{addr}> {msg}")
    # Process the command 
    commands = msg.split(" ")
    print(f"[DEBUG]: {commands}")
    if(commands[0] == ":authenticate"):
      state = authenticate(commands[1], commands[2])
      client_socket.send(str(state).encode(FORMAT))
      if state:
        connection_list.append(f"{commands[1]}: {addr}")
    
    if(commands[0] == ":register"):
      state = add_user(commands[1], commands[2])
      client_socket.send(str(state).encode(FORMAT))

    if(commands[0] == ":get_list"):
      client_socket.send(str(connection_list).encode(FORMAT))

    if msg == DISCONNECT_MSG:
      print("HERE")
      connected = False 
    else:
      print(f"[{addr}]: {msg}")



while True:
  (conn, addr) = s.accept()
  thread = threading.Thread(target=on_new_client, args=[conn, addr])
  thread.start()