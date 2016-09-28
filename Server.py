#!/usr/bin/env python

import threading
import socket
import Queue
import time
import json
import struct
import shelve
import sys
from thread import start_new_thread


def recv_size(the_socket):
    #data length is packed into 4 bytes
    total_len = 0;total_data = [];size = sys.maxint
    size_data = sock_data = ''; recv_size = 8192
    while total_len<size:
        sock_data = the_socket.recv(recv_size)
        if not total_data:
            if len(sock_data)>4:
                size_data += sock_data
                size = struct.unpack('>i', size_data[:4])[0]
                recv_size = size
                if recv_size>524288:
                    recv_size=524288
                total_data.append(size_data[4:])
            else:
                size_data += sock_data
        else:
            total_data.append(sock_data)
        total_len=sum([len(i) for i in total_data ])
    return ''.join(total_data)

def findUserNameByID(id):
    persistent_usernames = shelve.open('usernames.db', flag='r')
    return persistent_usernames[id]

def addUser(username):
    persistent_usernames = shelve.open('usernames.db')
    highest_id = len(persistent_usernames)
    persistent_usernames[str(highest_id+1)] = username
    return str(highest_id + 1)


HOST = socket.gethostname()
PORT = 5005
TYPE_JSON = 1;
TYPE_MESSAGE = 2;

cmd_q = Queue.Queue()
activeUser = {}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

#executor = Executor(cmd_q)
#executor.start()
s.listen(10)
print 'Socket now listening'

#Function for handling connections. This will be used to create threads
def clientthread(conn, queue):
    #Sending message to connected client
    conn.send('CONN_ACC') #send only takes string

    start_new_thread(clientInThread, (conn, queue))

def clientInThread(conn, in_q):
    out_q = Queue.Queue()
    start_new_thread(clientOutThread, (conn, out_q))

    while 1:
        data = recv_size(conn)
        jdata = json.loads(data)

        if 'user' in jdata:
            conn.send('\"user_added\" : %s' % addUser(jdata['user']))
        elif 'userID' not in jdata:
            conn.send('no authentication was provided. neither as an alias, nor as an ID')
        else:
            userAlias = findUserNameByID(jdata['userID'])
            jdata['user'] = userAlias

        if 'exit' in jdata:
            conn.send('connection terminated')
            break

        print jdata

        in_q.put((out_q, jdata))

        conn.send(json.dumps(jdata))

    conn.close()
    print 'connection closed to ' + jdata['user']

def clientOutThread(conn, out_q):
    while True:
        msg = out_q.get()
        conn.send(msg)
        time.sleep(20)

#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    clientthread(conn, cmd_q)
 
s.close()
