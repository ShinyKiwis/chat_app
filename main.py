import PySimpleGUI as sg
from database import *


# PEER CODE
import socket 

IP = socket.gethostbyname(socket.gethostname())
PORT = 3007 
ADDR = (IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = ":disconnect"
SIZE = 4096

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)



# ---------
active_list = []
global_username = ''


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
                  [sg.Listbox(values=['[binh]: Hello','[nguyen]: Hi'], expand_x=True, size=(0,15), key="chat_box", no_scrollbar=True)],
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

current_layout = "start"

def handle_register(username, password):
  client.send(f":register {username} {password}".encode(FORMAT))
  state = client.recv(SIZE).decode(FORMAT)
  return True if state == "True" else False

def handle_login(username, password):
  global current_layout
  global window
  # Send the username and password to authenticate
  client.send(f":authenticate {username} {password}".encode(FORMAT))
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


window = sg.Window('P2P Chat', layout)

def hide_register_layout():
  global current_layout
  global window
  window['col_register'].update(visible=False)
  current_layout = "start"
  window['col_start'].update(visible=True)


def handle_chat_layout(event, values):
  global current_layout
  global window
  # Get connection list
  client.send(":get_list".encode(FORMAT))
  addr_list = client.recv(SIZE).decode(FORMAT).split(" ")
  addr_list.pop(-1)
  for ele in addr_list:
    [addr_name, addr] = ele.split("-")
    tmp = addr.replace('(','').replace(')','').replace(' ','').replace('\'','').split(",")
    tmp[1] = int(tmp[1])
    user_conn = {
      f'{addr_name}': tuple(tmp)  
    }
    for user in active_list:
      for username,_ in user.items():
        if(username == addr_name):
          continue
    active_list.append(user_conn)
    print(active_list)
  #   print("12#!23123123")
  #   # active_list.append(tuple(tmp))



  # Update username 
  window['username'].update(f"Username: {values[0]}")
  window['left_col'].Widget.configure(borderwidth=1, relief=sg.DEFAULT_FRAME_RELIEF)
  # Logout 
  if event == "Logout":
    window['col_chat'].update(visible=False)
    current_layout="start"
    window['col_start'].update(visible=True)
    for idx, user in enumerate(active_list):
      for username,_ in user.items():
        if username == global_username:
          active_list.pop(idx)
          print(active_list)

  # Get friend list here and update it
  friends = []
  print(active_list)
  for user in active_list:
    for username,_ in user.items():
      if username not in friends and global_username != username:
        friends.append(username)
  window['friend_list'].update(values=friends)
  receiver = "Choose a user to start chatting" if len(values['friend_list']) == 0 else values['friend_list'][0] 
  window['receiver'].update(f"Receiver: {receiver}")

  # messages = []
  # receive messages
  # while True:
  #   window['chat'].update()



while True:
    event, values = window.read()
    # print(event, values)
    # Update active list when new connection established
    if event == sg.WIN_CLOSED:
        client.send(DISCONNECT_MSG.encode(FORMAT))
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
