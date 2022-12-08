import PySimpleGUI as sg
from database import *
import sys
import threading

# PEER CODE
import socket 

IP = socket.gethostbyname(socket.gethostname())
PORT = 3007 
ADDR = (IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = ":disconnect"
SIZE = 4096


active_list = {}
conn_list = {}
addr_list= []
name_list =[] 
global_username = ''
conn_idx = 0
global_peer = ''
global_log = {}

def on_new_connection(conn,flag):           #open listening thread and send thread
    connected=True
    while connected:
        if flag==1:
            msg=conn.recv(4096)
            msg=msg.decode(FORMAT)
            if msg=="file.msg":
                # receiver(conn)
                continue
            key_list = list(conn_list.keys())
            val_list = list(conn_list.values())
            pos = val_list.index(conn)
            # Find index in connection_list 
            # name = list(conn_list.values()).index(conn)
            name = key_list[pos]
            global_log[name].append(f'[{name}]: {msg}')
            # global_log[global_log[name][0]] = global_log[name][0].append(f'[{name}]: {msg}')
            print(global_log)

        else:
            #using same chat thread for all the peers connections and server connections
            #this thread call only once at the beginning of the connectiing to server phase
            msg=input()
            # if is_file==1:
            #     send_file(msg,connection_list[0])
            #     continue
            
            msg=msg.encode(FORMAT)
            #select sender from connection_list     #start from 0
            print("conidx: ",conn_idx)                         #print for testing
            conn_list[global_peer].send(msg)

# Client connect to central server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

# Thread for sending message
sender=threading.Thread(target=on_new_connection,args=(client,2,))
sender.start()


# listening socket only
LPORT = 0
lclient_addr=(IP,LPORT)
print(lclient_addr)
lclient=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    lclient.bind(lclient_addr)
    lclient.listen()
    lclient_addr = lclient.getsockname()
except socket.error as message:
    print('Bind failed. Error Code : '
          + str(message[0]) + ' Message '
          + message[1])
    sys.exit()


def connect_peer():                                     #listening for connection from other peer.
    while True:
        print("HERE")
        connection,addr=lclient.accept()
        # conn_list.append(connection)
        addr_list.append(addr)        

        identifier=connection.recv(1024).decode(FORMAT) #identifier first connection
        # name_list.append(identifier)                    #name list for active connection
        conn_list[identifier] = connection
        print("new peer connected: ",identifier)
        global_log[identifier] = []
        print("CONNETPEER:", global_log)
        #open listen thread only 
        
        new_sender=threading.Thread(target=on_new_connection,args=(connection,1,))      
        new_sender.start()
        
# ---------


sg.theme('DarkAmber')

start_layout = [[sg.Text('Welcome to P2P Chat')],
                [sg.Text('Invalid Credential',text_color="red", visible=False, key="error")],
                [sg.Text('Username: '), sg.Input()],
                [sg.Text('Password:  '), sg.Input(password_char="*")],
                [sg.Button('Login', pad=(10, 20)), sg.Button('Register')]]


friend_list_layout = [[sg.Text(key="username")],
                      [sg.Listbox(values=[], size=(20, 10), key="friend_list", no_scrollbar=False, enable_events=True)],
                      [sg.Button('Logout', pad=((0,0), (50,20)))]]

message_layout = [[sg.Text(key='receiver')],
                  [sg.Listbox(values=[], expand_x=True, size=(0,15), key="chat_box", no_scrollbar=True)],
                  [sg.Button("Upload"), sg.Input(), sg.Button('Send')]]

chat_layout = [[sg.Column(friend_list_layout, element_justification='c', key="left_col", pad=(20,20)),
                sg.Column(message_layout, key="right_col")]]

register_layout = [[sg.Text('Register your account')],
                   [sg.Text('User Existed!',text_color="red", visible=False, key="reg_error")],
                   [sg.Text('Username: '), sg.Input()],
                   [sg.Text('Password: '), sg.Input(password_char="*")],
                   [sg.Button('Back'),sg.Button('Register', pad=(10,20))]]

layout = [[sg.Column(start_layout, key="col_start", element_justification='c'), 
           sg.Column(chat_layout, key="col_chat", visible=False), 
           sg.Column(register_layout, key="col_register", visible=False, element_justification='c')]]


def handle_register(username, password):
  client.send(f":register {username} {password}".encode(FORMAT))
  state = client.recv(SIZE).decode(FORMAT)
  return True if state == "True" else False

def handle_login(username, password):
  global current_layout
  global window
  # Send the username and password to authenticate
  client.send(f":authenticate {username} {password} {lclient_addr}".encode(FORMAT))
  # Server return a string
  state = client.recv(SIZE).decode(FORMAT)
  if state == "False":
    window.Element("error").update(visible=True)
  else:
    global global_username
    # Update the connection_list
    window['col_start'].update(visible=False)
    window.Element("error").update(visible=False)
    current_layout='chat'
    window['col_chat'].update(visible=True)
    global_username = username



def hide_register_layout():
  global current_layout
  global window
  window['col_register'].update(visible=False)
  current_layout = "start"
  window['col_start'].update(visible=True)


def handle_chat_layout(event, values):
  global current_layout
  global window
  global global_peer
  # Get connection list
  client.send(":get_list".encode(FORMAT))
  addr_list = client.recv(SIZE).decode(FORMAT).strip().split(" ")
  temp_name = []
  print("addr_list: ", addr_list)
  print("active_list: ", active_list)
  # If there is changes in the connection_list, renew it
  for ele in addr_list:
    [addr_name, addr] = ele.split("-")
    temp_name.append(addr_name)
    if global_username == addr_name or addr_name in active_list:
      continue
    # Parse the message to tuple for chatting later
    tmp = addr.replace('(','').replace(')','').replace(' ','').replace('\'','').split(",")
    tmp[1] = int(tmp[1])
    active_list[f'{addr_name}'] = tuple(tmp)
  # Check if a user is remove 
  for username in active_list.keys():
    if username not in temp_name:
      active_list.pop(username)
      break
  # print(active_list
  #   # active_list.append(tuple(tmp))



  # Update username 
  window['username'].update(f"Username: {values[0]}")
  window['left_col'].Widget.configure(borderwidth=1, relief=sg.DEFAULT_FRAME_RELIEF)
  # Logout 
  if event == "Logout":
    window['col_chat'].update(visible=False)
    current_layout="start"
    window['col_start'].update(visible=True)
    # Remove user in central server
    client.send(DISCONNECT_MSG.encode(FORMAT)) 
    # Pop it in active list 
    # for idx, user in enumerate(active_list):
    #   for username,_ in user.items():
    #     if username == global_username:
    #       active_list.pop(idx)
          # print(active_list)

  # Get friend list here and update it
  friends = []
  # print(active_list)
  for username in active_list.keys():
    friends.append(username)

  window['friend_list'].update(values=friends)
  receiver = "Choose a user to start chatting" if len(values['friend_list']) == 0 else values['friend_list'][0] 
  window['receiver'].update(f"Receiver: {receiver}")
  # Check if in name list 
  if receiver != "Choose a user to start chatting":
    if receiver not in name_list:
      global_peer = receiver
      active_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      active_conn.bind((IP, 0))
      try:
        print("[DEBUG]: ", active_list[receiver])
        active_conn.connect(active_list[receiver]) 
        print("[DEBUG]: ", active_conn)
      except:
        print("LOI ME ROI")
      # Add to conn_list 
      conn_list[receiver] = active_conn
      # Append to name list 
      global_log[receiver] = []
      name_list.append(receiver)
      print(global_username)
      active_conn.send(global_username.encode(FORMAT))
      rec = threading.Thread(target=on_new_connection, args=(active_conn, 1,))
      rec.start()

    window['chat_box'].update(values=global_log[receiver]) 
  





current_layout = "start"
window = sg.Window('P2P Chat', layout)

def app_process(control):
    global current_layout
    if control == 1:
  # Main loop for GUI
      while True:
        event, values = window.read()
        print(event, values)
        # Update active list when new connection established
        if event == sg.WIN_CLOSED:
            client.send(DISCONNECT_MSG.encode(FORMAT))
            lclient.close()
            client.close()
            break
        elif event == "Register":
          window[f'col_{current_layout}'].update(visible=False)
          current_layout = "register"
          window[f'col_register'].update(visible=True)
        # Handle back to login screen
        if event == "Back" and current_layout == "register":
          hide_register_layout()

        # Handle Register 
        if event == "Register0" and current_layout == "register":
          print(values[3], values[4])
          state = handle_register(values[3], values[4])
          if state == True:
            hide_register_layout()
          else:
            window.Element("reg_error").update(visible=True)

        if event == "Login" and current_layout == "start":
          handle_login(values[0], values[1])

        # Handle chat message
        if current_layout == "chat":
          handle_chat_layout(event, values)
      window.close()
    else:
      connect_peer()

gui=threading.Thread(target=app_process,args=(1,))
chat_process=threading.Thread(target=app_process,args=(2,))
gui.start()
chat_process.start()

