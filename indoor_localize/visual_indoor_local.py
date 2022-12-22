import socket
import json
import matplotlib.pyplot as plt

host_ip = "192.168.50.169"
port = 8787

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect((host_ip, port))

x_coord = []
y_coord = []
ap_locations_list = [[0,0], [0, 5.7], [3.3, 0], [3.3, 5.7]]
ap_locations_x = [0, 0, 3.3, 3.3]
ap_locations_y = [0, 5.7, 0, 5.7]

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
    #for i in range(len(ap_locations_list)):
    plt.scatter(ap_locations_x, ap_locations_y, c='b')
    plt.scatter(x_coord, y_coord, c='r')
    plt.show()
    plt.pause(0.0001)
