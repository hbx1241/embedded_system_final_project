

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import websocket
import socket
try:
    import thread
except ImportError:
    import _thread as thread
import json

#Capture and parse ESP32 data from websocket in a json format
##connect to websocket
#websock_data = websocket.WebSocket()
#websock_data.connect("ws://192.168.4.1:81/")

def websocketparse():

    jresult = websock_data.recv()
    result = json.loads(jresult)
    temp = float(result['Temperature'])
    press = float(result['Pressure'])
    alt = float(result['Altitude'])
    hum = float(result['Humidity'])

    return temp,hum,press,alt

#Capture and parse ESP32 data from websocket in a json format
host = '192.168.187.193'
port = 8787
buffer_size = 1024
sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_data.bind((host, port))
#pare
def socketparse():
    #csv_data = sock_data.recv(buffer_size).decode('utf-8')
    #csv_data_parsed = csv_data.split(',')
    #temp = float(csv_data_parsed[0])
    #press = float(csv_data_parsed[1])
    #alt = float(csv_data_parsed[2])
    
    data = sock_data.recv(buffer_size).decode('utf-8')
    data_dict = json.load(data)
    dgx = data_dict["GYRO_XYZ"][0] 
    dt = data_dict["SAMPLE_NUM"]
    return dgx, dt 

#Create empty arrays
datatemp = []
datahum = []
datapress = []
dataalt = []

gx = []
t = []
#Fill empty arrays with initial values for each measurement
for x in range(50):
    #temp, hum, press = websocketparse()
    #temp, hum, press, alt = socketparse()

    #datatemp.append(temp)
    #datahum.append(hum)
    #datapress.append(press)
    #dataalt.append(alt)
    gx.append(x)
    t.append(x)

#Create plots
win = pg.GraphicsLayoutWidget()
win.setWindowTitle('pyqtgraph example: Scrolling Plots')
p1 = win.addPlot()
p1.setYRange(0, 40, padding=0)

p2 = win.addPlot()
p2.setYRange(0, 100, padding=0)

p3 = win.addPlot()
p3.setYRange(50, 120, padding=0)

p4 = win.addPlot()
p4.setYRange(50, 120, padding=0)

#Create lines for plot
curve1 = p1.plot(gx, pen=pg.mkPen('r', width=3))
curve2 = p2.plot(gx, pen=pg.mkPen('g', width=3))
curve3 = p3.plot(gx, pen=pg.mkPen('b', width=3))
curve4 = p4.plot(gx, pen=pg.mkPen('y', width=3))

ptr1 = 0

#update lists of measurments and add to plots
def updatelist():
    global datatemp,datahum,datapress,dataalt, curve1, curve2, curve3, curve4, ptr1
    global gx, t
    #temp, hum, press = websocketparse()
    #temp, hum, press, alt = socketparse()
    dgx, dt = socketparse()
    
    gx[:-1] = gx[1:]
    gx[-1] = dgx 
    curve1.setData(gx)
    curve2.setData(gx)
    curve3.setData(gx)
    curve4.setData(gx)
    ##temperature plot
    #datatemp[:-1] = datatemp[1:]
    #datatemp[-1] = temp
    #curve1.setData(datatemp)

    ## humitidy plot
    #datahum[:-1] = datahum[1:]
    #datahum[-1] = hum
    #curve2.setData(datahum)

    ## pressure plot
    #datapress[:-1] = datapress[1:]
    #datapress[-1] = press
    #curve3.setData(datapress)

    ## alt plot
    #dataalt[:-1] = dataalt[1:]
    #dataalt[-1] = alt
    #curve4.setData(dataalt)



    ptr1 += 1


# update all plots
def updateplot():
    updatelist()


timer = pg.QtCore.QTimer()
timer.timeout.connect(updateplot)
timer.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec()
