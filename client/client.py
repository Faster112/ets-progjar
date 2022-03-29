import socket
import select
import sys
from threading import Thread
import tqdm

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip_address = '127.0.0.1'
port = 8081
server.connect((ip_address, port))
exit_flag = False

def downloadzip(sock):
    with open ('shared.zip', 'wb') as f:
        print("Downloading shared.zip...")
        with open('shared.zip', 'wb') as f:
            # print(sock.recv(40960))
            data = f.write(sock.recv(40960))
            while data:
                data = f.write(sock.recv(40960))
    f.close()

def send_message(sock):
    while True:
        message = sys.stdin.readline()
        sock.send(message.encode())
        if message == 'EXIT\n':
            exit_flag = True
            break
        elif message[0] == "LIST\n":
            continue
        elif message[0] == "LOG\n":
            continue
        elif message[0] == "DOWNZIP\n":
            continue
        elif message[0] == "SEND\n":
            continue
        sys.stdout.write('<You> ')
        sys.stdout.write(message)
        sys.stdout.flush()

def recv_message(sock):
    while True:
        if exit_flag:
            break
        message = sock.recv(2048).decode()
        if message == "DOWNLOAD" or message == "DOWNLOAD\n":
            downloadzip(sock)
            break
        sys.stdout.write(message)
        sys.stdout.flush()

Thread(target=send_message, args=(server,)).start()
Thread(target=recv_message, args=(server,)).start()

while True:
    if exit_flag:
        break
    socket_list = [server]
    read_socket, write_socket, error_socket = select.select(socket_list, [], [])
    for socks in socket_list:
        if socks == server:
            send_message(socks)
        else:
            recv_message(socks)

server.close()