import socket
import json
import matplotlib.pyplot as plt

host_ip = "192.168.0.113"
port = 8787

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect((host_ip, port))

x_coord = []
y_coord = []
ap_locations_list = [[0.1,0], [4,0], [0,2.5], [4,2.5]]

plt.ion()
fig = plt.figure(figsize=(3,3))
#ax = fig.subplots(1,1)
while True:
    data = client_socket.recv(1024).decode('utf-8')
    print(data)
    try:
        data_json = json.loads(data)
    except:
        print("fail to load data")
        continue
    
    x_coord.append(data_json["x_coord"])
    y_coord.append(data_json["y_coord"])
    x_coord = x_coord[-20:]
    y_coord = y_coord[-20:]
    fig.clear()
    for i in len(ap_locations_list):
        plt.plot(ap_locations_list[i][0], ap_locations_list[i][1], 'b')
    plt.plot(x_coord, y_coord, 'r')
    plt.show()
    plt.pause(0.0001)
