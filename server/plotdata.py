import socket
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import pandas as pd

HOST = '192.168.187.193'# IP address
PORT = 8787 # Port to listen on (use ports > 1023)

LAST = 10 # show last LAST data
t = []
t2 = []
gyro = [[] for i in range(3)]
acc = [[] for i in range(3)]
mag = [[] for i in range(3)]
color = [['r', 'g', 'b']]
dimension = ['X', 'Y', 'Z']

file = "recorded_data"
df = pd.read_csv(file + ".txt")
df2 = pd.read_csv(file + "_vh.txt")
#file = "sit_down"
#df = pd.read_csv("./data/" + file + "/" + file + "_6.txt")
#df2 = pd.read_csv("_" + file + "_vh.txt")
for i in range(len(df["x"])):
    t.append(i)
for i in range(len(df2["v"])):
    t2.append(i)
acc[0] = df["x"]
acc[1] = df["y"]
acc[2] = df["z"]
v = df2["v"]
h = df2["h"]

plt.plot(t, acc[0], t, acc[1], t, acc[2], t2, v, t2, h)

plt.show()


 
