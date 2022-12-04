import socket
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from threading import *
import threading
import time
import queue
import pandas as pd

HOST = '192.168.176.193'# IP address
PORT = 8787 # Port to listen on (use ports > 1023)

LAST = 1200 # show last LAST data
t = []
humi = []
pres = []
temp = []
acc = [[] for i in range(3)]


q = queue.Queue()
event = threading.Event()
stop = threading.Event()
def plotdata():
    event.wait()
    color = [['r', 'g', 'b']]
    dimension = ['X', 'Y', 'Z']

    list = []
    t = []
    id = 0
    while id < 240:
        while q.qsize() > 0:
            list.append(q.get())
            t.append(id)
            id += 1
            print(id)
            #print(list)
        #list = list[-LAST:]
        #t = list[-LAST:]
    out = []
    id = 0
    for i in list:
        out.append(i)

    df = pd.DataFrame(out, columns= ["x", "y", "z"])
    df.to_csv("dataout.txt")
    stop.set()
          
def getdata():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print("Starting server at: ", (HOST, PORT))
    conn, addr = s.accept()
    event.set()
    obj = []
    while stop.is_set() == False:
        data = conn.recv(1024).decode('utf-8')
        #print("Received from socket server:", data)
        try:
            obj = json.loads(data)

        except:
            print("warning: fail to load json")
        q.put([float(obj['AC'][0])/1000 * 9.806, float(obj['AC'][1])/1000 * 9.806, float(obj['AC'][2])/1000 * 9.806])
    event.clear()

    
t1=Thread(target=getdata)
t2=Thread(target=plotdata)
t1.start()
t2.start()
