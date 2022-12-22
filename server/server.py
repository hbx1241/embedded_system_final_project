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
import random
from paho.mqtt import client as mqtt_client

setting = open("setting.json")

setting = json.load(setting)
HOST = setting["HOST"]# IP address
PORT = int(setting["PORT"]) # Port to listen on (use ports > 1023)
URL = setting["URL"] # ifttt url
username = setting["username"] # username of public mqtt server
password = setting["password"] # password

SAMPLE_RATE = 20
LAST = 500 * SAMPLE_RATE # show last LAST data
seq_len = 8
t = []
acc = [[] for i in range(3)]
act = ["idle", "walk", "stand_up", "sit_down", "fall_forward"]
# MQTT

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def mqtt_publish(client, light_on):
    # msg = "gesture detected!"

    result = client.publish(topic, light_on)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send light_on == `{light_on}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

broker = 'broker.emqx.io'
port = 1883
topic = "light switching"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'


client = connect_mqtt()
client.loop_start()

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
            if (id > SAMPLE_RATE + 10):
               v = float(np.dot(list[-1:], av) / lav) 
               avt = (v / lav) * av
               aht = list[-1:] - avt
               h = float(np.sqrt(np.dot(aht, aht.T)))
               vh.append([v, h])
            if (id % seq_len == 0 and id > 2 * SAMPLE_RATE):
                z = []
                for hmm in model:
                    score = hmm.score(vh[-seq_len:])
                    z.append(score)
                print(z)
                prediction = act[z.index(max(z))]
                print(prediction, id)
                if prediction == "fall_forward":
                    print("fall fall_detected")
                    # requests.get(url = URL)

        if not len(av) and id > SAMPLE_RATE:
            print("v set!")
            av = np.average(list[0:SAMPLE_RATE-1], axis=0)
            lav = np.sqrt(np.dot(av, av))
    df = pd.DataFrame(list, columns= ["x", "y", "z"])
    df.to_csv("recorded_data.txt")
#    df2 = pd.DataFrame(vh, columns= ["v", "h"])
#    df2.to_csv("recorded_data_vh.txt")
    print("data saved!")

def gesture_recognition(acc_data, gesturing, light_on):
    SVM = np.linalg.norm(np.array(acc_data))
    # finite state machine
    # given current state(gesturing) and input(SVM), determine next state
    if (not gesturing):
        if (SVM > 1.8*9.8): # gesture detected
            light_on = not light_on
            mqtt_publish(client, light_on)
            gesturing = True
    else:
        if(SVM < 12):
            gesturing = False
    return gesturing, light_on


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
    gesturing = False
    light_on = True
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
                    acc_data = [float(obj['AC'][0])/1000 * 9.806, float(obj['AC'][1])/1000 * 9.806, \
                    float(obj['AC'][2])/1000 * 9.806]
                    # if (obj['M']):
                    if (obj['S']):
                        gesturing, light_on = gesture_recognition(acc_data, gesturing, light_on)
                    else: 
                        q.put(acc_data)
        except Exception as e:
            # print("warning: fail to load json ", e, str)
            print()
        
    event.clear()
    s.close()
    

t1=Thread(target=getdata)
t2=Thread(target=plotdata)
for a in act:
    with open("./model/" + a + ".pkl", "rb") as file:
        q.put(pickle.load(file))
t1.start()
t2.start()
