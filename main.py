import PySimpleGUI as sg
from database import *

sg.theme('DarkAmber')

start_layout = [[sg.Text('Welcome to P2P Chat')],
                [sg.Text('Invalid Credential',text_color="red", visible=False, key="error")],
                [sg.Text('Username: '), sg.Input()],
                [sg.Text('Password:  '), sg.Input(password_char="*")],
                [sg.Button('Login', pad=(10, 20)), sg.Button('Register')]]

friend_list_layout = [[sg.Text(key="username")],
                      [sg.Listbox(values=[], size=(20, 10), key="friend_list")],
                      [sg.Button('Logout', pad=((0,0), (50,20)))]]

message_layout = [[sg.Text('MessageBox')]]

chat_layout = [[sg.Column(friend_list_layout, element_justification='c', key="left_col", pad=(20,20)),
                sg.Column(message_layout)]]
register_layout = [[sg.Text('Register your account')],
                   [sg.Text('Username: '), sg.Input()],
                   [sg.Text('Password: '), sg.Input(password_char="*")],
                   [sg.Button('Back'),sg.Button('Register', pad=(10,20))]]

layout = [[sg.Column(start_layout, key="col_start", element_justification='c'), 
           sg.Column(chat_layout, key="col_chat", visible=False), 
           sg.Column(register_layout, key="col_register", visible=False, element_justification='c')]]

current_layout = "start"

def handle_register(username, password):
  add_user(username, password)

def handle_login(username, password):
  global current_layout
  global window
  state = authenticate(username, password)
  if state == False:
    window.Element("error").update(visible=True)
  else:
    window['col_start'].update(visible=False)
    current_layout='chat'
    window['col_chat'].update(visible=True)


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
  # Update username 
  window['username'].update(f"Username: {values[0]}")
  window['left_col'].Widget.configure(borderwidth=1, relief=sg.DEFAULT_FRAME_RELIEF)
  # Logout 
  if event == "Logout":
    window['col_chat'].update(visible=False)
    current_layout="start"
    window['col_start'].update(visible=True)

  # Get friend list here and update it
  friends = ["binh", "duy", "anna"]
  window['friend_list'].update(values=friends)


while True:
    event, values = window.read()
    print(event, values)
    # Handle back to login screen
    if event == "Back" and current_layout == "register":
      hide_register_layout()

    # Handle Register 
    if event == "Register0" and current_layout == "register":
      handle_register(values[2], values[3])
      hide_register_layout()

    if event == "Login" and current_layout == "start":
      handle_login(values[0], values[1])

    # Handle chat message
    if current_layout == "chat":
      handle_chat_layout(event, values)


    if event == sg.WIN_CLOSED:
        break
    elif event == "Register":
      window[f'col_{current_layout}'].update(visible=False)
      current_layout = "register"
      window[f'col_register'].update(visible=True)
    

window.close()
