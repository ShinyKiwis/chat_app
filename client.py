import socket 
import threading
import sys
import os
import tqdm

#for file transfering
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024 * 4 #4KB

HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, 3007)  



FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "OUT"


# client server connection only
host=socket.gethostbyname(socket.gethostname())                 
client_server_addr=(host,5200)
client_server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

try:
    client_server.bind(client_server_addr)
except socket.error as message:
    print('Bind failed. Error Code : '
          + str(message[0]) + ' Message '
          + message[1])
    sys.exit()



# listening socket only
lclient_addr=(host,5250)
lclient=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    lclient.bind(lclient_addr)
except socket.error as message:
    print('Bind failed. Error Code : '
          + str(message[0]) + ' Message '
          + message[1])
    sys.exit()



conn_idx=0          # flag to decide sending to who, default = 0 means connect to server.
is_file=0          # flag to determine if sending file or message



######################## TO SEND FILE ######################
def send_file(filename,s):
    # get the file size
    filesize = os.path.getsize(filename)
    # create the client socket
    """
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #print(f"[+] Connecting to {host}:{port}")
    s.connect(addr)
    print("[+] Connected.")
    """
    # send the filename and filesize
    s.send("file.msg".encode(FORMAT))         #send identifier as  file sending
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                f.close()
                break
            # we use sendall to assure transimission in 
            # busy networks
            s.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    return
    # close the socket
    #s.close()

#############################################################

################### TO RECEIVE FILE #########################
def receiver(s):
    # receive the file infos
    # receive using client socket, not server socket
    received = s.recv(BUFFER_SIZE).decode()                        #HERER
    print(received)
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)
    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    new_filename="new_"+filename

    with open(new_filename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = s.recv(BUFFER_SIZE)                           #HERER
            if  len(bytes_read)!=BUFFER_SIZE:    
                # nothing is received
                # file transmitting is done
                f.close()
                break
            # write to the file the bytes we just received
            print(len(bytes_read))
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    print("file rec done") 
    return
    # close the client socket
    #client_socket.close()
    # close the server socket
    
#file receiving  



#############################################################








def on_new_connection(conn,flag):           #open listening thread and send thread
    connected=True
    while connected:
        if flag==1:
            msg=conn.recv(4096)
            msg=msg.decode(FORMAT)
            if msg=="file.msg":
                receiver(conn)
                continue
            print(msg)
        else:
            #using same chat thread for all the peers connections and server connections
            #this thread call only once at the beginning of the connectiing to server phase
            msg=input()
            if is_file==1:
                send_file(msg,connection_list[0])
                continue
            
            msg=msg.encode(FORMAT)
            #select sender from connection_list     #start from 0
            print("conidx: ",conn_idx)                         #print for testing
            connection_list[0].send(msg)



def connect_server():                          
    client_server.connect(ADDR)                 #connect to server.
    connection_list.append(client_server)       # add server connection to connection list
    addr_list.append(ADDR)
    print(addr_list)                            #test
    global conn_idx
    conn_idx = 1                  #conn_idx of the server in the connection list is 1
    """
    client_server.send(addr).encode(FORMAT)
    """
    if connection_list[0]==client_server: print("yes")
    sender=threading.Thread(target=on_new_connection,args=(client_server,2,))     
    #thread for sending to the server
    #using 1 thread to send for all the peer connections and server connections
    receiver=threading.Thread(target=on_new_connection,args=(client_server,1,))     #thread for receiving from the server
    sender.start()
    receiver.start()


#passively connect
def connect_peer():                                     #listening for connection from other peer.
    while True:
        connection,addr=lclient.accept()
        connection_list.append(connection)
        addr_list.append(addr)

        identifier=connection.recv(4096).decode(FORMAT) #identifier first connection
        name_list.append(identifier)                    #name list for active connection
        print("new peer connected: ",identifier)

        #open listen thread only 
        
        new_sender=threading.Thread(target=on_new_connection,args=(connection,1,))      
        new_sender.start()
        



def handle_socket(flag):
    if flag==1:
        connect_peer()
    else:
        connect_server()











lclient.listen()                        #open listening socket


connection_list=[]                      #these three contain unique values
addr_list=[]                           #not use yet since conn list for sending + name list to identify
name_list=[]                    

peerl=threading.Thread(target=handle_socket,args=(1,))
peers=threading.Thread(target=handle_socket,args=(2,))
peerl.start()       
peers.start()

selected_name="tam"         #choosing new connection by name #testing only


#list of new connection to test , test_conn_list for "tam"
test_conn_list=[(host,20000),(host,30000),(host,40000)]            
connect_flag=0



while True:
    if selected_name not in name_list:                  #if not in active conn name list
        active_conn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)        #create new socket
        active_port=0
        active_conn.bind((host,active_port))                                #bind with available port
      
        name_list.append(selected_name)
        try:  
            active_conn.connect(test_conn_list[connect_flag])                   # new socket connection to port
        except:
            continue
        #append new connection to connection list
                                           #add to list      
        connection_list.append(active_conn)                                 # add new connection to active list
        addr_list.append(test_conn_list[connect_flag])
        #send identifier
        identifier_msg=selected_name.encode(FORMAT)                         #send self.identifier to new connected peer
        active_conn.send(identifier_msg)
        rec=threading.Thread(target=on_new_connection,args=(active_conn,1))     #start new thread to hear from new connected peer
        rec.start()
    else:
        continue

