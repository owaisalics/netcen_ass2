import sys
import threading
import argparse
import socket
import os
import time
import base64
import json

def send_msg(conn, msg):
    serialized = json.dumps(msg).encode('utf-8')
    x=len(serialized) 
    x=str(x)
    x=x+'\n'
    
    x=bytes(x,encoding='utf-8')
    conn.send(x)
    
    #conn.send(b'%d\n' % len(serialized))
    
 #   xx='%d\n'.format(len(serialized) )
#    conn.send(bytes(xx,encoding='ascii'))
    conn.sendall(serialized)

def get_file_list(client_dir):
    files = os.listdir(client_dir)
    files = [file for file in files if os.path.isfile(os.path.join(client_dir, file))]
    file_list = {}
    for file in files:
        path = os.path.join(client_dir, file)
        mtime = os.path.getmtime(path)
        ctime = os.path.getctime(path)
        file_list[file] = max(ctime, mtime)

    return file_list

def send_new_file(conn, filename):
    with open(filename, "rb") as file:
        data = base64.b64encode(file.read()).decode('utf-8')
        msg = {
            'type': 'file_add',
            'filename': filename,
            'data': data
        }
        send_msg(conn, msg)

def send_delete_file(conn, filename):
    msg = {
        'type': 'file_delete',
        'filename': filename
    }
    send_msg(conn, msg)

def get_changes(client_dir, last_file_list):
    file_list = get_file_list(client_dir)
    changes = {}
    for filename, mtime in file_list.items():
        if filename not in last_file_list or last_file_list[filename] < mtime:
            changes[filename] = 'file_add'

    for filename, time in last_file_list.items():
        if filename not in file_list:
            changes[filename] = 'file_delete'

    return (changes, file_list)

def handle_dir_change(conn, changes):
    for filename, change in changes.items():
        if change == 'file_add':
            print('new file added ', filename)
            send_new_file(conn, filename)
        elif change == 'file_delete':
            print('file deleted ', filename)
            send_delete_file(conn, filename)

def watch_dir(conn, client_dir, handler):
    last_file_list = {}
    while True:
        time.sleep(1)
        changes, last_file_list = get_changes(client_dir, last_file_list)
        handler(conn, changes)


def get_message(s):
    length_str = b''
    char = s.recv(1)
    while char != b'\n':
        length_str += char
        char = s.recv(1)
    total = int(length_str)
    off = 0
    msg = b''
    while off < total:
        temp = s.recv(total - off)
        off = off + len(temp)
        msg = msg + temp
    return json.loads(msg.decode('utf-8'))

def add_file(client_dir,filename,data):
    path = os.path.join(client_dir, filename)
    with open(path, 'wb') as file:
        file.write(base64.b64decode(data.encode('utf-8')))

def delete_file(client_dir, filename):
    print ("m here")
    path = os.path.join(client_dir, filename)
    if os.path.exists(filename):
        os.remove(path)


def handle_srvr(s, client_dir):  #from servr usr to client local
    print ("at here")
    while True:
        msg=get_message(s)
        
        if msg['type'] == 'file_add':
            add_file(client_dir, msg['filename'], msg['data'])
        
        elif msg['type'] == 'file_delete':
            delete_file(client_dir, msg['filename'])
          
    s.close()

def client(server_addr, server_port, uname, client_dir):
    s = socket.socket()
    s.connect((server_addr, server_port))
    #s.send("client1")
    send_msg(s,uname)
    #s.send(username)
    print ("sent username")
    send_msg(s,os.getcwd())
    print("sent directory")
    #print rep
    threading.Thread(target=watch_dir, args=(s, client_dir, handle_dir_change)).start()#from client local to servr
    threading.Thread(target=handle_srvr,args=(s,os.getcwd() ) ).start()    #from client on server to local client dir
  #  watch_dir(s, client_dir, handle_dir_change)
   # s.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("server_addr", help="Address of the server.")
    parser.add_argument("server_port", type=int, help="Port number the server is listening on.")
    parser.add_argument("username", type=str, help="username of client")
    args = parser.parse_args()
#    usrnme=args.username
    client(args.server_addr, args.server_port, args.username, os.getcwd())#from client to local to server
