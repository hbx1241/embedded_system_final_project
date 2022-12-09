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
import pickle
import requests

HOST = '192.168.176.193'# IP address
PORT = 8787 # Port to listen on (use ports > 1023)
URL = 'https://maker.ifttt.com/trigger/fall_detected/json/with/key/bZ5RcrGNtpyWza0jDm1KzZ'  # ifttt url

SAMPLE_RATE = 20
LAST = 500 * SAMPLE_RATE # show last LAST data
t = []
acc = [[] for i in range(3)]
act = ["idle", "walk", "stand_up", "sit_down", "fall_forward", "sit", "lay"]

q = queue.Queue()
event = threading.Event()
stop = threading.Event()

def plotdata():
    dimension = ['X', 'Y', 'Z']
    model = []
    while q.qsize() > 0:
        model.append(q.get())
    list = []
    t = []
    av = []
    vh = []
    lav = 0 
    id = 0
    event.wait()
    while stop.is_set() == False:
        while q.qsize() > 0:
            list.append(q.get())
            t.append(id)
            id += 1
            if (id > SAMPLE_RATE + 1):
               v = float(np.dot(list[-1:], av) / lav) 
               avt = (v / lav) * av
               aht = list[-1:] - avt
               h = float(np.sqrt(np.dot(aht, aht.T)))
               vh.append([v, h])
            if (id % SAMPLE_RATE == 0 and id > 2 * SAMPLE_RATE):
                z = []
                for hmm in model:
                    score = hmm.score(vh[-SAMPLE_RATE:])
                    z.append(score)
                print(z)
                prediction = act[z.index(max(z))]
                print(prediction, id)
                if prediction == "fall_forward":
                    print("fall fall_detected")
                    #requests.get(url = URL)

        if not len(av) and id > SAMPLE_RATE:
            print("v set!")
            av = np.average(list[0:SAMPLE_RATE-1], axis=0)
            lav = np.sqrt(np.dot(av, av))
    df = pd.DataFrame(list, columns= ["x", "y", "z"])
    df.to_csv("recorded_data.txt")
    df2 = pd.DataFrame(vh, columns= ["v", "h"])
    df2.to_csv("recorded_data_vh.txt")
    print("data saved!")
          
def getdata():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print("Starting server at: ", (HOST, PORT))
    conn, addr = s.accept()
    conn.settimeout(5)
    event.set()
    obj = []
    cur = 0
    last = 0
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            str = data.rsplit(";")
        except:
            stop.set()
            break
        #print("Received from socket server:", data)
        try:
            for d in str:
                if len(d) != 0:
                    obj = json.loads(d)
                    q.put([float(obj['AC'][0])/1000 * 9.806, float(obj['AC'][1])/1000 * 9.806, \
                    float(obj['AC'][2])/1000 * 9.806])
        except Exception as e:
            print("warning: fail to load json ", e, str)
        
    event.clear()
    s.close()
    

t1=Thread(target=getdata)
t2=Thread(target=plotdata)
for a in act:
    with open("./model/" + a + ".pkl", "rb") as file:
        q.put(pickle.load(file))
t1.start()
t2.start()
