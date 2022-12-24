import random
import RPi.GPIO as GPIO
from paho.mqtt import client as mqtt_client


broker = 'broker.emqx.io'
port = 1883
topic = "light switching"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'thomas'
password = 'aaa'


def connect_mqtt() -> mqtt_client:
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


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        topic = msg.topic
        msg = msg.payload.decode()
        light_idx = msg[0]
        light_on = msg[1:]
        print(light_idx, light_on)
        print(f"Received `{msg}` from `{topic}` topic")
        if light_idx == '1':
            if light_on == 'True':
                GPIO.output(11,True)
            elif light_on == 'False':
                GPIO.output(11,False)
        elif light_idx == '2':
            if light_on == 'True':
                GPIO.output(15,True)
            elif light_on == 'False':
                GPIO.output(15, False)


        
    client.subscribe(topic)
    client.on_message = on_message


def run():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)    # 將P1接頭的11腳位設定為輸出
    GPIO.output(11, True)   # turn on the light initially
    GPIO.setup(15, GPIO.OUT)
    GPIO.output(15, True)

    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
