import socket
import threading
import sys
import os
import tqdm


FORMAT="utf-8"
host=socket.gethostbyname(socket.gethostname())
ADDR=(host,3007)

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    server.bind(ADDR)
except socket.error as message:
    print('Bind failed. Error Code : '
          + str(message[0]) + ' Message '
          + message[1])
    sys.exit()

server.listen()



def on_new_connection(conn,addr):
    connected=True
    while connected:
        try:
            request=conn.recv(4096).decode(FORMAT)
        except:
            print(addr," disconnected!")
            connection_list.remove(conn)
            addr_list.remove(addr)
            return
            
        if request=="1":
            for i in addr_list:
                #connect to database to get name
                msg="("+i[0]+", "+str(i[1])+")"
                msg=msg.encode(FORMAT)
                conn.send(msg)
        elif request=="connect":
            msg="send who nig?".encode(FORMAT)
            conn.send(msg)
            msg=conn.recv(4096).decode(FORMAT)
        elif request=="file.msg":
            receiver(conn)
            continue



# file receiving
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
def receiver(client_socket):
    # receive the file infos
    # receive using client socket, not server socket
    received = client_socket.recv(BUFFER_SIZE).decode()                        #HERER
    print(received)
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)
    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    new_filename="new"+filename

    with open(new_filename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)                           #HERER
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
    


connection_list=[]
addr_list=[]
while True:
    conn,addr=server.accept()
    connection_list.append(conn)
    addr_list.append(addr)
    print(addr_list)
    print("New connection [",addr,"] connected!\n")
    print("Total connection: ",len(connection_list))
    thread=threading.Thread(target=on_new_connection,args=(conn,addr,))
    thread.start()


