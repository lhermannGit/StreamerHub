#!/usr/bin/env python

import threading
import socket
import Queue
import time
from thread import start_new_thread
from Executor import Executor

HOST = '192.168.1.9'
PORT = 5005

cmd_q = Queue.Queue()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

executor = Executor(cmd_q)
executor.start()
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
    while True:
        data = conn.recv(1024)

	print data
        if not data:
            break
        query = data.split(" ")

        in_q.put((out_q, query))

        conn.send("RECVD : " + data)
        time.sleep(20)

    conn.close()

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
