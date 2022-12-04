import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from matplotlib.figure import Figure
from tkinter import *
from tkinter import ttk
import time
import serial
import threading
import socket
import json
import numpy as np
import matplotlib.pyplot as plot

HOST = '192.168.187.193' # IP address
PORT = 8787 # Port to listen on (use ports > 1023)

ApplicationGL = False

class ServerSettings:
    HOST = '127.0.0.1'
    PORT = 8787
class IMU:
    Roll = 0
    Pitch = 0
    Yaw = 0



myserver = ServerSettings()
myimu  = IMU()

def RunAppliction():
    global ApplicationGL
    myserver.HOST = Port_entry.get()
    myserver.PORT = Baud_entry.get()
    ApplicationGL = True
    ConfWindw.destroy()

ConfWindw = Tk()
ConfWindw.title("Waiting for connection")
ConfWindw.configure(bg = "#2E2D40") 
ConfWindw.geometry('700x300')
ConfWindw.resizable(width=False, height=False)
positionRight = int(ConfWindw.winfo_screenwidth()/2 - 300/2)
positionDown = int(ConfWindw.winfo_screenheight()/2 - 150/2)
ConfWindw.geometry("+{}+{}".format(positionRight, positionDown))

Port_label = Label(text = "HOST:",font =("",12),justify= "right",bg = "#2E2D40",fg = "#FFFFFF")
Port_label.place(x = 50, y =30,anchor = "center")
Port_entry = Entry(width = 20,bg = "#37364D", fg = "#FFFFFF", justify = "center")
Port_entry.insert(INSERT,myserver.HOST)
Port_entry.place(x = 180, y = 30,anchor = "center")

Baud_label = Label(text = "PORT:",font =("",12),justify= "right",bg = "#2E2D40",fg = "#FFFFFF")
Baud_label.place(x = 50, y =80,anchor = "center")
Baud_entry = Entry(width = 20,bg = "#37364D", fg = "#FFFFFF", justify = "center")
Baud_entry.insert(INSERT,str(myserver.PORT))
Baud_entry.place(x = 180, y = 80,anchor = "center")

ok_button = Button(text = "Ok",width = 8,command = RunAppliction,bg="#135EF2",fg ="#FFFFFF")
ok_button.place(x = 150, y = 120,anchor="center")

def InitPygame():
    global display
    pygame.init()
    display = (640,480)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption('IMU visualizer   (Press Esc to exit)')


def InitGL():
    glClearColor((1.0/255*46),(1.0/255*45),(1.0/255*64),1)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    gluPerspective(100, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0,0.0, -5)


def DrawText(textString):     
    font = pygame.font.SysFont ("Courier New",25, True)
    textSurface = font.render(textString, True, (255,255,0), (46,45,64,255))     
    textData = pygame.image.tostring(textSurface, "RGBA", True)         
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)    

def DrawBoard():
    
    glBegin(GL_QUADS)
    x = 0
    
    for surface in surfaces:
        
        for vertex in surface:  
            glColor3fv((colors[x]))          
            glVertex3fv(vertices[vertex])
        x += 1
    glEnd()

def DrawGL():

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity() 
    gluPerspective(90, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0,0.0, -5)   

    glRotatef(round(myimu.Pitch,1), 0, 0, 1)
    glRotatef(round(myimu.Roll,1), -1, 0, 0)

    DrawText("Roll: {}°               Pitch: {}°".format(round(myimu.Roll,1),round(myimu.Pitch,1)))
    DrawBoard()
    pygame.display.flip()

def SerialConnection ():
    global serial_object
    serial_object = serial.Serial( myport.Name, baudrate= myport.Speed, timeout = myport.Timeout)

def ReadData():
    while True:
        
        serial_input = serial_object.readline()
        if(len(serial_input) == 9 and serial_input[0] == 0x24 ): 
            X = [serial_input[2], serial_input[1]]
            Ax = int.from_bytes(X,byteorder = 'big',signed=True)

            Y = [serial_input[4], serial_input[3]]
            Ay = int.from_bytes(Y,byteorder = 'big',signed=True)

            myimu.Roll = Ax/16384.0*90
            myimu.Pitch = Ay/16384.0*90

def InitConnection():
    global socket_server;
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_server.bind((HOST, PORT))
    socket_server.listen()
    print("Starting server at: ", (HOST, PORT))
    global conn;
    conn, addr = socket_server.accept()
    with conn:
        print("Connected at", addr)

def ReadDataWifi():
    global obj_json
    while True:
        data = conn.recv(1024).decode('utf-8')
        print("Received from socket server:", data)
        obj_json = json.loads(data)

        X = [obj_json['GYRO_XYZ'][1]/10000, obj_json['GYRO_XYZ'][1]/10000]
        Ax = int.from_bytes(X,byteorder = 'big',signed=True)

        Y = [obj_json['GYRO_XYZ'][2]/10000, obj_json['GYRO_XYZ'][2]/10000]
        Ay = int.from_bytes(Y,byteorder = 'big',signed=True)

        myimu.Roll = Ax/16384.0*90
        myimu.Pitch = Ay/16384.0*90
def main():
    ConfWindw.mainloop()
    if ApplicationGL == True:

        InitPygame()
        InitGL()
        

        try:
            #SerialConnection()
            InitConnection()
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
            myThread1 = threading.Thread(target = ReadDataWifi)
            myThread1.daemon = True
            myThread1.start() 
            while True:
                event = pygame.event.poll()
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    break 

                DrawGL()
                pygame.time.wait(150)

        except:
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            DrawText("Sorry, something is wrong :c")
            pygame.display.flip()
            time.sleep(5)

                 


if __name__ == '__main__': main()
