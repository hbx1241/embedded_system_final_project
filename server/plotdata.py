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
humi = []
pres = []
temp = []
gyro = [[] for i in range(3)]
acc = [[] for i in range(3)]
mag = [[] for i in range(3)]
color = [['r', 'g', 'b']]
dimension = ['X', 'Y', 'Z']

df = pd.read_csv("dataout.txt")
for i in range(len(df["x"])):
    t.append(i)
acc[0] = df["x"]
acc[1] = df["y"]
acc[2] = df["z"]


plt.plot(t, acc[0], t, acc[1], t, acc[2])

plt.show()


 
