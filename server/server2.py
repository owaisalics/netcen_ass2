import sys
import argparse
import socket
import time
import os
import threading
import base64
import json
usrnme=[]
all_clients=[]
c_dir=[]
all_c_dir=[]

def get_user_dir(server_dir, addr):
    path = os.path.join(server_dir, str(usrnme) )
#    path = os.path.join(server_dir, addr[0] + "_" + str(addr[1]))
    os.makedirs(path, exist_ok=True)
    return path

def add_file(client_dir, filename, data):
    path = os.path.join(client_dir, filename)
#    if not os.path.exists(path):
    with open(path, 'wb') as file:
        file.write(base64.b64decode(data.encode('utf-8')))
    if filename=="Sharefile.dropbin":
        
        path=os.path.join(os.getcwd(), "Sharefile.dropbin")
        
        
        with open(path,'ab') as file:
            data=base64.b64decode(data.encode('utf-8'))+b'\n'
            file.write(data)
        file.close()
#            file.write(b'\n')

def delete_file(client_dir, filename):
    path = os.path.join(client_dir, filename)
    if os.path.exists(path):
        os.remove(path)

def get_message(conn):
    length_str = b''
    char = conn.recv(1)
    while char != b'\n':
        length_str += char
        char = conn.recv(1)
    total = int(length_str)
    off = 0
    msg = b''
    while off < total:
        temp = conn.recv(total - off)
        off = off + len(temp)
        msg = msg + temp
    return json.loads(msg.decode('utf-8'))

def handle_client(conn, client_dir):
    while True:
        msg = get_message(conn)
        if msg['type'] == 'file_add':
            print('file added ', os.path.join(client_dir, msg['filename']))
            add_file(client_dir, msg['filename'], msg['data'])

#            for x in all_clients:             #####################
            ####path = os.path.join(os.getcwd(), "shared folder" )  #####################
         
           #### add_file(path, msg['filename'], msg['data'])    #####################
        elif msg['type'] == 'file_delete':
            print('file deleted ', os.path.join(client_dir, msg['filename']))
            delete_file(client_dir, msg['filename'])
 #           for x in all_clients:             #####################
         ####   path = os.path.join(os.getcwd(), "shared folder")  #####################
         
          ####  delete_file(path, msg['filename'])    #####################           
    conn.close()


def get_file_list(client_dir):                  #usr on srvr to shared folder
    print ("inside snding files list code")
    #os.path.join(os.path.getcwd(), )
    files = os.listdir(client_dir)
    files = [file for file in files if os.path.isfile(os.path.join(client_dir, file))]
    file_list = {}
    for file in files:
        path = os.path.join(client_dir, file)
        mtime = os.path.getmtime(path)
        ctime = os.path.getctime(path)
        file_list[file] = max(ctime, mtime)

    return file_list


def get_file_list2(client_dir):                 #may be usr on servr to local client dir
#    os.path.join(os.path.getcwd(),client_dir )
    files = os.listdir(client_dir)
    files = [file for file in files if os.path.isfile(os.path.join(client_dir, file))]
    file_list = {}
    for file in files:
        path = os.path.join(client_dir, file)
        mtime = os.path.getmtime(path)
        ctime = os.path.getctime(path)
        file_list[file] = max(ctime, mtime)

    return file_list

def add_file2(shared_dir, filename, data):          #from usr on srvr to shard foldr
    path = os.path.join(shared_dir, filename)
    if not os.path.exists(path):
        with open(path, 'wb') as file:
            file.write(base64.b64decode(data.encode('utf-8')))



def delete_file2(shared_dir, filename):             #from usr on srvr to shard foldr
    path = os.path.join(shared_dir, filename) 
    if os.path.exists(path):
        os.remove(path)

def send_new_file(filename,usernme):        #from user on server to shared folder
    client_dir=os.path.join(os.getcwd(), str(usernme) )
    path = os.path.join(client_dir, filename)
    print("inside code to copy in shrd foldr")
    with open(path, "rb") as file:
        data = base64.b64encode(file.read()).decode('utf-8')
        msg = {
            'type': 'file_add',
            'filename': filename,
            'data': data
        }
#        send_msg(conn, msg)
        shared_dir=os.path.join(os.getcwd(), str("shared folder"))
        add_file2(shared_dir, msg['filename'], msg['data'])


def send_delete_file( filename,usrnme):        #link from user to shared foldre
    msg = {
        'type': 'file_delete',
        'filename': filename
    }
    print("insdie dleting from shared foldr")
#    send_msg(conn, msg)
    shared_dir=os.path.join(os.getcwd(), str("shared folder"))
    delete_file2(shared_dir, msg['filename'])

    #add_file(shared_dir, msg['filename'], msg['data'])



def get_changes(usrnme, last_file_list):        ###for user on servr to servr's shard folder
    print ("gtng chnges")
    path=os.path.join(os.getcwd(),usrnme)
    file_list = get_file_list(path)
    changes = {}
    for filename, mtime in file_list.items():
        if filename not in last_file_list:# or last_file_list[filename] < mtime:
            changes[filename] = 'file_add'

    for filename, time in last_file_list.items():
        if filename not in file_list:
            changes[filename] = 'file_delete'

    return (changes, file_list)

def get_changes2(usrnme, last_file_list):        ### 2:server usr to client local
    path=os.path.join(os.getcwd(), usrnme)
    file_list = get_file_list2(path)#########################33
    changes = {}
    for filename, mtime in file_list.items():
        if filename not in last_file_list:# or last_file_list[filename] < mtime:
            changes[filename] = 'file_add'

    for filename, time in last_file_list.items():
        if filename not in file_list:
            changes[filename] = 'file_delete'

    return (changes, file_list)

def handler(changes,usernme):               #from usr on servr to shared foldr
    print ("in hndlr")
    for filename, change in changes.items():
        if change == 'file_add':
            print('new file added ', filename)
            send_new_file(filename,usernme)
            print ("printng name ")#############
            print (filename)######################
        elif change == 'file_delete':
            print('file deleted ', filename)
            send_delete_file(filename,usernme)

def watch_users(connec,usernme):        #from user on srvr to shared foldr
    print("watchin")
    last_file_list = {}
    while True:
        time.sleep(1)
        #cl_path=os.path.join(os.getcwd(), str(usernme) )
        changes, last_file_list = get_changes(usrnme, last_file_list)
        handler(changes,usernme)


def send_msg(s,msg):
    serialized = json.dumps(msg).encode('utf-8')
    x=len(serialized) 
    x=str(x)
    x=x+'\n'
    
    x=bytes(x,encoding='utf-8')
    s.send(x)
   
    
#    s.send(b'%d\n' % len(serialized))
    s.sendall(serialized)

def snd_new_file(s,filename,usrnme):
    client_dir=os.path.join(os.getcwd(), str(usrnme) )
    path = os.path.join(client_dir, filename)

    with open(path, "rb") as file:
        data = base64.b64encode(file.read()).decode('utf-8')
        msg = {
            'type': 'file_add',
            'filename': filename,
            'data': data
        }
        send_msg(s, msg)
    
def snd_delete_file(s,filename):
    msg = {
        'type': 'file_delete',
        'filename': filename
    }
    send_msg(s, msg)


def handler_d(s,changes,usrnme):                   #for usr on servr to local dir of client
    for filename, change in changes.items():
        if change == 'file_add':
            print('new file added 2', filename)
            snd_new_file(s, filename,usrnme)
        elif change == 'file_delete':
            print('file deleted ', filename)
###############################

            path=os.path.join(os.getcwd(),"Sharefile.dropbin")
            sfiles=[]
            with open(path, "r") as file:
                for line in file:
                    words = line.split()
                    sfiles.append(words[0])
                    if filename==words[0]:
                        for i in range(1,len(words)):
                            userr=words[i]
                   #         print(userr)
                            path=os.path.join(os.getcwd(), userr)
                            path=os.path.join(path, filename)
                            if os.path.exists(path):
                                os.remove(path)
                    #            print("yp")
#                                path=os.path.join(os.getcwd(), usrnme)
 #                               path=os.path.join(path, shared_file)
                    
                file.close()
                  #      print
            #if filename in sfiles:
###############################
            
                
            snd_delete_file(s, filename)


def c_to_local(s, usrnme):                   #from user on servr to client local
    print("kd")
    last_file_list={}
    while True:
        time.sleep(5)
        changes, last_file_list = get_changes2(usrnme, last_file_list)
        handler_d(s, changes,usrnme)
    
def shared_to_usr(conn,usrnme):              #####################sharing from shared to usr on srver thru sharefile dropbin
    print ("PPPPPPP")
    while True:
        time.sleep(3)
        path=os.path.join(os.getcwd(),usrnme)
        path=os.path.join(path,"Sharefile.dropbin")
        
        if os.path.isfile(path):
            #print("yse")
            with open(path, "r") as file:
                #print("ya")
                for line in file:
                    line_words=line.split()
                    shared_file=line_words[0]
                 #   print (shared_file)
                    path=os.path.join(os.getcwd(),usrnme)
                    path=os.path.join (path, shared_file)
                    if os.path.isfile(path):
                  #      print("HMM")
                        for i in range(1,len(line_words)):
                            userr=line_words[i]
                   #         print(userr)
                            path=os.path.join(os.getcwd(), userr)
                            if os.path.exists(path):
                    #            print("yp")
                                path=os.path.join(os.getcwd(), usrnme)
                                path=os.path.join(path, shared_file)
                                with open(path,'rb') as file2:
                                    data = base64.b64encode(file2.read()).decode('utf-8')
    
    #                                data = file.base64.b64encode(file.read()).decode('utf-8')
                                    msg = {
                                      #  'type': 'file_add',
                                        'filename': shared_file,
                                        'data': data
                                    }
                                    add_file(os.path.join(os.getcwd(),userr),msg['filename'],msg['data'])
            file.close()            
        path=os.path.join(os.getcwd(),usrnme)
        path=os.path.join(path,"Selectfile.dropbin")
        
        if os.path.isfile(path):
            sfiles = []         #Selectedfiles
            with open(path, "r") as file:
                for line in file:
                    words = line.split()
                    sfiles.append(words[0])
                file.close()
            path=os.path.join(os.getcwd(),usrnme)
            path=os.path.join(path,"Sharefile.dropbin")
        
            with open(path, "r") as file:
                for line in file:
                    line_words = line.split()
                    shared_file = line_words[0]
                    #if os.path.isfile(os.path.join(client_dir, shared_file)):
                    
                    if os.path.isfile(os.path.join(os.path.join(os.getcwd(), usrnme), shared_file)):
                        for i in range(1,len(line_words)):
                            user = line_words[i]
                            #Delete this file from this user 
                            path=os.path.join(os.getcwd(), user)
                            path = os.path.join(path, shared_file)
                            if os.path.exists(path):
                                os.remove(path)
                            
                           # send_delshared_file(conn,user,shared_file)
            file.close()
            
            
            
        #else:
        
#        add_file(shared_dir, msg['filename'], msg['data'])

            #     data = file.read()#base64.b64encode(file.read()).decode('utf-8')
            #     msg = {
            #         'type': 'file_add',
            # #        'filename': filename,
            #         'data': data
            #     }
            # print (msg['data'])





        
def server(port, server_dir):
    host = socket.gethostbyname(socket.gethostname())

    s = socket.socket()
    s.bind((host, port))
    s.listen(10)

    print("Host ", host, " is listening on ", port)

    while True:
        conn, addr = s.accept()

#	all_addr={}
#	all_addr.append(addr)
        print("Got connection form ", addr)
#        usrnme=conn.recv(20)
#        print usrnme
#        print usrnme
        global usrnme
 #       usrnme=conn.recv(1024)
  #      print (usrnme)
        usrnme=get_message(conn)
        print (usrnme)
   #     print (usrnme)
        global all_clients
        all_clients.append(usrnme)



        print ("total users r")
        print (all_clients)

        global c_dir
        c_dir=get_message(conn)
        global all_c_dir
        all_c_dir.append(c_dir)


        threading.Thread(target=handle_client, args=(conn, get_user_dir(server_dir, addr))).start()

#        threading.Thread(target=watch_users, args=(conn,usrnme) ).start() #sharing from users on server to shared folder
        threading.Thread(target=c_to_local, args=(conn,usrnme)).start() #sharing from users on server to local client dir
        threading.Thread(target=shared_to_usr, args=(conn,usrnme) ).start()        #sharing to user on srver from sharefile.dropbin

    s.close()
        
if __name__ == "__main__":
#    usrnme=[]
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, help="Port number the server will listen on.")
    args = parser.parse_args()
    server(args.port, os.getcwd())

