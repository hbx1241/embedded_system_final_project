#!/usr/bin/env python3
import time
import socket 

HOST = '127.0.0.1'
PORT =  8787

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

num = 1
while True:
    for i in (1, 360):
        outdata = "{\"x\":%d, \"y\":%d, \"z\":%d, \"s\":%d}" %(i, 360 - i, i * (360 - i) / 360, num)
        s.send(outdata.encode())
        num += 1 
        time.sleep(1)
        
