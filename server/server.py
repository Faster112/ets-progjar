# chat server
import socket
import select
import sys
import threading
import os 
from zipfile import ZipFile
import pickle

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ip_address = '127.0.0.1'
port = 8081
server.bind((ip_address, port))
server.listen(100)
list_of_clients = []
chats = []

def listfile(conn):
    files = ''
    for file in os.listdir("./shared"):
        files += file + ' '
    conn.send(("<Server> " + files + '\n').encode())

def chatlog(conn):
    conn.send("<Server>\n".encode())
    for chat in chats:
        conn.send(('\t' + chat).encode())
    conn.send("</Server>\n".encode())

def downloadzip(conn):
    with ZipFile('shared.zip', 'w') as zip:
        for file in os.listdir("./shared"):
            zip.write("./shared/" + file)
    conn.send("DOWNLOAD\n".encode())
    conn.send(str(os.path.getsize('shared.zip')).encode())
    with open('shared.zip', 'rb') as f:
        data = f.read(40960)
        while data:
            conn.send(data)
            data = f.read(40960)
    # pickle.dump(open("shared.zip", 'rb'))
    # with open ('shared.zip', 'rb') as f:
    #     data = f.read(4096)
    #     conn.send(data)
    # sleep(2)
    f.close()
    os.remove('shared.zip')

def clientthread(conn, addr):
    conn.send("Welcome to this chatroom!\n".encode())
    while True:
        try:
            data = conn.recv(2048).decode()
            message = data.split(' ')
            if data:
                if message[0] == "EXIT\n":
                    remove(conn)
                    break
                elif message[0] == "LIST\n":
                    listfile(conn)
                    continue
                elif message[0] == "LOG\n":
                    chatlog(conn)
                    continue
                elif message[0] == "DOWNZIP\n":
                    downloadzip(conn)
                    continue
                elif message[0] == "SEND\n":
                    continue
                message_to_send = "<" + addr[0] + ":" + str(addr[1]) + "> " + data
                chats.append(message_to_send)
                print(message_to_send, end="")
                broadcast(message_to_send, conn)
            else:
                remove(conn)
        except:
            break

def broadcast(message, connection):
    for clients in list_of_clients:
        if clients != connection:
            try:
                clients.send(message.encode())
            except:
                clients.close()
                remove(clients)

def remove(connection):
    if connection in list_of_clients:
        broadcast(message="<" + connection.getpeername()[0] + ":" + str(connection.getpeername()[1]) + "> has left the chatroom.\n", connection=connection)
        list_of_clients.remove(connection)

while True:
    conn, addr = server.accept()
    list_of_clients.append(conn)
    print("<" + addr[0] + ":" + str(addr[1]) + "> connected")
    threading.Thread(target=clientthread, args=(conn, addr)).start()

conn.close()