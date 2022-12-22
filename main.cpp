/* Sockets Example
 * Copyright (c) 2016-2020 ARM Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <algorithm>
#include <cstdio>
#include <stdlib.h>
#include <string.h>
#include "mbed.h"
#include "stm32l475e_iot01.h"
#include "wifi_helper.h"
#include "mbed-trace/mbed_trace.h"

// Sensors drivers present in the BSP library
#include "stm32l475e_iot01_tsensor.h"
#include "stm32l475e_iot01_hsensor.h"
#include "stm32l475e_iot01_psensor.h"
#include "stm32l475e_iot01_magneto.h"
#include "stm32l475e_iot01_gyro.h"
#include "stm32l475e_iot01_accelero.h"

#include <events/mbed_events.h>
#include "ble/BLE.h"
#include "ble/Gap.h"
#include "ButtonService.h"
#include "LEDService.h"
#include "pretty_printer.h"
#include <ble/gatt/GattCharacteristic.h>

// TODO change your server ip and port
#define SERVER_IP "192.168.30.193"
#define SERVER_PORT 8787
// TODO time interval between each sending message
#define TIME_INTERVAL 1s
#define FLAG1 (1UL << 0)
#define FLAG2 (1UL << 2)
#if MBED_CONF_APP_USE_TLS_SOCKET
#include "root_ca_cert.h"



#ifndef DEVICE_TRNG
#error "mbed-os-example-tls-socket requires a device which supports TRNG"
#endif
#endif // MBED_CONF_APP_USE_TLS_SOCKET

InterruptIn button(BUTTON1);

volatile int mode = 0;

class SocketDemo;
DigitalOut led(LED1);
EventFlags event_flags;
EventQueue eq;
void read_sensor(char *buffer, int sample_num);

class SocketDemo {
    static constexpr size_t MAX_NUMBER_OF_ACCESS_POINTS = 10;
    static constexpr size_t MAX_MESSAGE_RECEIVED_LENGTH = 100;

#if MBED_CONF_APP_USE_TLS_SOCKET
    static constexpr size_t REMOTE_PORT = 443; // tls port
#else
    static constexpr size_t REMOTE_PORT = 80; // standard HTTP port
#endif // MBED_CONF_APP_USE_TLS_SOCKET

public:
    SocketDemo(events::EventQueue &event_queue) : 
        _net(NetworkInterface::get_default_instance()),
        _event_queue(event_queue)
    {
    }

    ~SocketDemo()
    {
        if (_net) {
            _net->disconnect();
        }
    }

    void run()
    {
        if (!_net) {
            printf("Error! No network interface found.\r\n");
            return;
        }

        /* if we're using a wifi interface run a quick scan */
        if (_net->wifiInterface()) {
            /* the scan is not required to connect and only serves to show visible access points */
            wifi_scan();

            /* in this example we use credentials configured at compile time which are used by
             * NetworkInterface::connect() but it's possible to do this at runtime by using the
             * WiFiInterface::connect() which takes these parameters as arguments */
        }

        /* connect will perform the action appropriate to the interface type to connect to the network */

        printf("Connecting to the network...\r\n");

        nsapi_size_or_error_t result = _net->connect();
        if (result != 0) {
            printf("Error! _net->connect() returned: %d\r\n", result);
            return;
        }

        print_network_info();

        /* opening the socket only allocates resources */
        result = _socket.open(_net);
        if (result != 0) {
            printf("Error! _socket.open() returned: %d\r\n", result);
            return;
        }

#if MBED_CONF_APP_USE_TLS_SOCKET
        result = _socket.set_root_ca_cert(root_ca_cert);
        if (result != NSAPI_ERROR_OK) {
            printf("Error: _socket.set_root_ca_cert() returned %d\n", result);
            return;
        }
        _socket.set_hostname(MBED_CONF_APP_HOSTNAME);
#endif // MBED_CONF_APP_USE_TLS_SOCKET

        /* now we have to find where to connect */

        SocketAddress address;

        if (!address.set_ip_address(SERVER_IP)) {
            return;
        }

        address.set_port(SERVER_PORT);

        /* we are connected to the network but since we're using a connection oriented
         * protocol we still need to open a connection on the socket */

        printf("Opening connection to remote port %d\r\n", REMOTE_PORT);

        result = _socket.connect(address);
        if (result != 0) {
            printf("Error! _socket.connect() returned: %d\r\n", result);
            return;
        }

        /* exchange an HTTP request */
        int sample_num = 0;
        printf("waiting to start\n");
        
        _event_queue.call_every(
            50ms,
            [this] {
                send_http_request();
            }
        );
        /*while (1) {
            if (!send_http_request(sample_num)) {
                break;
                //ThisThread::sleep_for(10s);
                //continue;
            }
            
            printf("--- Sending of message No.%d is successful ---\r\n", sample_num);
            sample_num++;
            ThisThread::sleep_for(80ms);
        }*/
        Timer t;
        t.start();
        _event_queue.dispatch_forever();
        auto us = t.elapsed_time().count();
        printf("%llu \n", us);
        printf("Socket run has finished\r\n");
    }

private:
    bool resolve_hostname(SocketAddress &address)
    {
        const char hostname[] = MBED_CONF_APP_HOSTNAME;

        /* get the host address */
        printf("\nResolve hostname %s\r\n", hostname);
        nsapi_size_or_error_t result = _net->gethostbyname(hostname, &address);
        if (result != 0) {
            printf("Error! gethostbyname(%s) returned: %d\r\n", hostname, result);
            return false;
        }

        printf("%s address is %s\r\n", hostname, (address.get_ip_address() ? address.get_ip_address() : "None") );

        return true;
    }

    bool send_http_request()
    {
        /* loop until whole request sent */
        /*const char head[] = "GET / HTTP/1.1\r\n"
                            "Host: ifconfig.io\r\n"
                            "Connection: close\r\n"
                            "\r\n";
        */
        static int sample_num = 0;
        char *buffer = (char *) malloc(sizeof(char) * 80);
        buffer[0] = '\0';
        //strcat(buffer, head);
        read_sensor(buffer, sample_num);

        nsapi_size_t bytes_to_send = strlen(buffer);
        nsapi_size_or_error_t bytes_sent = 0;

        //printf("\r\nSending message: \r\n%s", buffer);

        while (bytes_to_send) {
            bytes_sent = _socket.send(buffer + bytes_sent, bytes_to_send);
            if (bytes_sent < 0) {
                printf("Error! _socket.send() returned: %d\r\n", bytes_sent);
                return false;
            } else {
                //printf("sent %d bytes\r\n", bytes_sent);
            }

            bytes_to_send -= bytes_sent;
        }

        free(buffer);
        //printf("Complete message sent\r\n");
        sample_num++;
        return true;
    }

    bool receive_http_response()
    {
        char buffer[MAX_MESSAGE_RECEIVED_LENGTH];
        int remaining_bytes = MAX_MESSAGE_RECEIVED_LENGTH;
        int received_bytes = 0;

        /* loop until there is nothing received or we've ran out of buffer space */
        nsapi_size_or_error_t result = remaining_bytes;
        while (result > 0 && remaining_bytes > 0) {
            result = _socket.recv(buffer + received_bytes, remaining_bytes);
            if (result < 0) {
                printf("Error! _socket.recv() returned: %d\r\n", result);
                return false;
            }

            received_bytes += result;
            remaining_bytes -= result;
        }

        /* the message is likely larger but we only want the HTTP response code */

        //printf("received %d bytes:\r\n%.*s\r\n\r\n", received_bytes, strstr(buffer, "\n") - buffer, buffer);

        return true;
    }

    void wifi_scan()
    {
        WiFiInterface *wifi = _net->wifiInterface();

        WiFiAccessPoint ap[MAX_NUMBER_OF_ACCESS_POINTS];

        /* scan call returns number of access points found */
        int result = wifi->scan(ap, MAX_NUMBER_OF_ACCESS_POINTS);

        if (result <= 0) {
            printf("WiFiInterface::scan() failed with return value: %d\r\n", result);
            return;
        }

        printf("%d networks available:\r\n", result);

        for (int i = 0; i < result; i++) {
            printf("Network: %s secured: %s BSSID: %hhX:%hhX:%hhX:%hhx:%hhx:%hhx RSSI: %hhd Ch: %hhd\r\n",
                   ap[i].get_ssid(), get_security_string(ap[i].get_security()),
                   ap[i].get_bssid()[0], ap[i].get_bssid()[1], ap[i].get_bssid()[2],
                   ap[i].get_bssid()[3], ap[i].get_bssid()[4], ap[i].get_bssid()[5],
                   ap[i].get_rssi(), ap[i].get_channel());
        }
        printf("\r\n");
    }

    void print_network_info()
    {
        /* print the network info */
        SocketAddress a;
        _net->get_ip_address(&a);
        printf("IP address: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
        _net->get_netmask(&a);
        printf("Netmask: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
        _net->get_gateway(&a);
        printf("Gateway: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
    }

private:
    NetworkInterface *_net;
    events::EventQueue &_event_queue;
#if MBED_CONF_APP_USE_TLS_SOCKET
    TLSSocket _socket;
#else
    TCPSocket _socket;
#endif // MBED_CONF_APP_USE_TLS_SOCKET
};

void read_sensor(char *buffer, int sample_num)
{
    float sensor_value = 0;
    int16_t pDataXYZ[3] = {0};
    float pGyroDataXYZ[3] = {0};
    //char inner_buf[50];

    //printf("buffer: %s\n", buffer);
    //printf("\n\tNew loop, LED1 should blink during sensor read\n");

    led = 1;

    //strcat(buffer, "\n{\n");

    /*sensor_value = BSP_TSENSOR_ReadTemp();
    snprintf(inner_buf, 50, "\t\"TEMPERATURE\": %.2f, \n", sensor_value);
    strcat(buffer, inner_buf);

    sensor_value = BSP_HSENSOR_ReadHumidity();
    snprintf(inner_buf, 50, "\t\"HUMIDITY\": %.2f, \n", sensor_value);
    strcat(buffer, inner_buf);

    sensor_value = BSP_PSENSOR_ReadPressure();
    snprintf(inner_buf, 50, "\t\"PRESSURE\": %.2f, \n", sensor_value);
    strcat(buffer, inner_buf);*/

    //led = 0;

    //ThisThread::sleep_for(1s);

    //led = 1;

    /*BSP_MAGNETO_GetXYZ(pDataXYZ);
    snprintf(inner_buf, 50, "\t\"MAGNETO_XYZ\": [%d, %d, %d], \n", pDataXYZ[0], pDataXYZ[1], pDataXYZ[2]);
    strcat(buffer, inner_buf);*/

    BSP_ACCELERO_AccGetXYZ(pDataXYZ);
    snprintf(buffer, 80, "{\n\t\"AC\": [%d, %d, %d],\t\"S\": %d\n,\t\"M\": %d\n};", \
                pDataXYZ[0], pDataXYZ[1], pDataXYZ[2], sample_num, mode);
    //strcat(buffer, inner_buf);

    return;
}

void button_pressed()
{
    mode = mode ? 0 : 1;
}

const static char DEVICE_NAME[] = "Button";

static EventQueue event_queue(/* event count */ 10 * EVENTS_EVENT_SIZE);


class BatteryDemo : ble::Gap::EventHandler {
public:
    BatteryDemo(BLE &ble, events::EventQueue &event_queue) :
        _ble(ble),
        _event_queue(event_queue),
        _led1(LED1, 1),
        _led2(LED2, 0),
        _button(BLE_BUTTON_PIN_NAME, BLE_BUTTON_PIN_PULL),
        _button_service(NULL),
        _button_uuid(ButtonService::BUTTON_SERVICE_UUID),
        _led_service(NULL),
        _led_uuid(LEDService::LED_SERVICE_UUID),
        _adv_data_builder(_adv_buffer) { }

    ~BatteryDemo() {
        delete _led_service;
    }

    void start() {
        _ble.gap().setEventHandler(this);

        _ble.init(this, &BatteryDemo::on_init_complete);

        _event_queue.call_every(500, this, &BatteryDemo::blink);

        _event_queue.dispatch_forever();
    }

private:
    /** Callback triggered when the ble initialization process has finished */
    void on_init_complete(BLE::InitializationCompleteCallbackContext *params) {
        if (params->error != BLE_ERROR_NONE) {
            printf("Ble initialization failed.");
            return;
        }

        print_mac_address();

        /* Setup primary service. */

        _button_service = new ButtonService(_ble, false); /* initial value for button pressed */
        // _led_service = new LEDService(_ble, false);
        _led_service = new LEDService(_ble);

        _button.fall(Callback<void()>(this, &BatteryDemo::button_pressed));
        _button.rise(Callback<void()>(this, &BatteryDemo::button_released));

        _ble.gattServer().onDataWritten(this, &BatteryDemo::on_data_written);

        start_advertising();
    }

    void start_advertising() {
        /* Create advertising parameters and payload */

        ble::AdvertisingParameters adv_parameters(
            ble::advertising_type_t::CONNECTABLE_UNDIRECTED,
            ble::adv_interval_t(ble::millisecond_t(1000))
        );

        _adv_data_builder.setFlags();
        _adv_data_builder.setLocalServiceList(mbed::make_Span(&_button_uuid, 1));
        _adv_data_builder.setName(DEVICE_NAME);

        /* Setup advertising */

        ble_error_t error = _ble.gap().setAdvertisingParameters(
            ble::LEGACY_ADVERTISING_HANDLE,
            adv_parameters
        );

        if (error) {
            print_error(error, "_ble.gap().setAdvertisingParameters() failed");
            return;
        }

        error = _ble.gap().setAdvertisingPayload(
            ble::LEGACY_ADVERTISING_HANDLE,
            _adv_data_builder.getAdvertisingData()
        );

        if (error) {
            print_error(error, "_ble.gap().setAdvertisingPayload() failed");
            return;
        }

        /* Start advertising */

        error = _ble.gap().startAdvertising(ble::LEGACY_ADVERTISING_HANDLE);

        if (error) {
            print_error(error, "_ble.gap().startAdvertising() failed");
            return;
        }
    }

    void button_pressed(void) {
        _event_queue.call(Callback<void(bool)>(_button_service, &ButtonService::updateButtonState), true);
    }

    void button_released(void) {
        _event_queue.call(Callback<void(bool)>(_button_service, &ButtonService::updateButtonState), false);
    }

    void on_data_written(const GattWriteCallbackParams *params) {
        // wish to receive more than one char... so using array to store
        const uint8_t* value = params->data;
        printf("Receive value ");
        for(int i=0; i<9;i++){
            printf("%c", value[i]);
        }
        printf("\r\n");
        if (params->handle == _led_service->getValueHandle()) {
	        if (value[0] == 0x30) {
                _led2.write(0);
            } else if (value[0] == 0x31) {
                _led2.write(1);
            }
        }
    }

    void blink(void) {
        _led1 = !_led1;
    }

private:
    /* Event handler */

    virtual void onDisconnectionComplete(const ble::DisconnectionCompleteEvent&) {
        _ble.gap().startAdvertising(ble::LEGACY_ADVERTISING_HANDLE);
    }

private:
    BLE &_ble;
    events::EventQueue &_event_queue;

    DigitalOut  _led1;
    DigitalOut  _led2;
    InterruptIn _button;

    ButtonService *_button_service;
    UUID _button_uuid;
    LEDService *_led_service;
    UUID _led_uuid;

    uint8_t _adv_buffer[ble::LEGACY_ADVERTISING_MAX_SIZE];
    ble::AdvertisingDataBuilder _adv_data_builder;
};

/** Schedule processing of events from the BLE middleware in the event queue. */
void schedule_ble_events(BLE::OnEventsToProcessCallbackContext *context) {
    event_queue.call(Callback<void()>(&context->ble, &BLE::processEvents));
}

int main() {
    printf("\nStart sensor init\n");

    /*BSP_TSENSOR_Init();
    BSP_HSENSOR_Init();
    BSP_PSENSOR_Init();

    BSP_MAGNETO_Init();*/
    BSP_GYRO_Init();
    BSP_ACCELERO_Init();
    button.fall(&button_pressed);

    printf("\r\nStarting socket\r\n\r\n");

#ifdef MBED_CONF_MBED_TRACE_ENABLE
    mbed_trace_init();
#endif

    SocketDemo *socket = new SocketDemo(eq);
    MBED_ASSERT(socket);
    socket->run();

    BLE &ble = BLE::Instance();
    ble.onEventsToProcess(schedule_ble_events);

    BatteryDemo demo(ble, event_queue);
    demo.start();
    
    return 0;
}