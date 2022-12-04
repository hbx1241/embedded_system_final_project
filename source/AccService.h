#ifndef __BLE_MAGNETO_SERVICE_H__
#define __BLE_MAGNETO_SERVICE_H__

#include <stdio.h>
#include "mbed.h"
#include "stm32l475e_iot01_accelero.h"
#include "ble/BLE.h"
#include <cstdint>

class AccService {
public:
    const static uint16_t ACC_SERVICE_UUID        = 0xA002;
    const static uint16_t ACC_CHARACTERISTIC_UUID = 0xA003;
    //const static uint16_t MAGNETOY_CHARACTERISTIC_UUID = 0xA004;
    //const static uint16_t MAGNETOZ_CHARACTERISTIC_UUID = 0xA005;

    AccService(BLE &_ble) :
        ble(_ble), 
        AccCharacteristic(  ACC_CHARACTERISTIC_UUID, (uint8_t *) acc, 
                                (uint16_t) sizeof(acc), (uint16_t) sizeof(acc), 
                                GattCharacteristic::BLE_GATT_CHAR_PROPERTIES_NOTIFY)
        /*magnetoYCharacteristic( MAGNETOY_CHARACTERISTIC_UUID, (uint8_t *) magnetoY, 
                                (uint16_t) sizeof(magnetoY), (uint16_t) sizeof(magnetoY),
                                GattCharacteristic::BLE_GATT_CHAR_PROPERTIES_NOTIFY),
        magnetoZCharacteristic( MAGNETOZ_CHARACTERISTIC_UUID, (uint8_t *) magnetoZ, 
                                (uint16_t) sizeof(magnetoZ), (uint16_t) sizeof(magnetoZ),
                                GattCharacteristic::BLE_GATT_CHAR_PROPERTIES_NOTIFY)*/
    {
        static bool serviceAdded = false; /* We should only ever need to add the information service once. */
        if (serviceAdded) {
            return;
        }
        GattCharacteristic *charTable[] = { &AccCharacteristic 
                                            /*&magnetoYCharacteristic, 
                                            &magnetoZCharacteristic*/ };
        GattService         AccService(AccService::ACC_SERVICE_UUID, charTable, sizeof(charTable) / sizeof(GattCharacteristic *));
        ble.gattServer().addService(AccService);

        serviceAdded = true;
    }

    void updateAcc(int16_t newAcc[3]) {
        memset(acc, '\0', 20);
        sprintf(acc, "%d,%d,%d;", newAcc[0], newAcc[1], newAcc[2]);
        ble.gattServer().write(AccCharacteristic.getValueHandle(), (uint8_t *) acc, sizeof(acc));
    }

    /*void updateMagnetoY(int16_t newMagneto) {
        sprintf(magnetoY, "%d unit", newMagneto);
        ble.gattServer().write(magnetoYCharacteristic.getValueHandle(), (uint8_t *) magnetoY, sizeof(magnetoY));
    }

    void updateMagnetoZ(int16_t newMagneto) {
        sprintf(magnetoZ, "%d unit", newMagneto);
        ble.gattServer().write(magnetoZCharacteristic.getValueHandle(), (uint8_t *) magnetoZ, sizeof(magnetoZ));
    }*/

private:
    BLE &ble;
    char acc[20];
    /*char magnetoY[10];
    char magnetoZ[10];*/
    GattCharacteristic    AccCharacteristic;
    /*GattCharacteristic    magnetoYCharacteristic;
    GattCharacteristic    magnetoZCharacteristic;*/
};

#endif 