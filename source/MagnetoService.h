#ifndef __BLE_MAGNETO_SERVICE_H__
#define __BLE_MAGNETO_SERVICE_H__

#include <stdio.h>
#include "mbed.h"
#include "stm32l475e_iot01_magneto.h"
#include "ble/BLE.h"
#include <cstdint>

class MagnetoService {
public:
    const static uint16_t MAGNETO_SERVICE_UUID        = 0xA002;
    const static uint16_t MAGNETO_CHARACTERISTIC_UUID = 0xA003;
    //const static uint16_t MAGNETOY_CHARACTERISTIC_UUID = 0xA004;
    //const static uint16_t MAGNETOZ_CHARACTERISTIC_UUID = 0xA005;

    MagnetoService(BLE &_ble) :
        ble(_ble), 
        magnetoCharacteristic(  MAGNETO_CHARACTERISTIC_UUID, (uint8_t *) magneto, 
                                (uint16_t) sizeof(magneto), (uint16_t) sizeof(magneto), 
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
        GattCharacteristic *charTable[] = { &magnetoCharacteristic 
                                            /*&magnetoYCharacteristic, 
                                            &magnetoZCharacteristic*/ };
        GattService         magnetoService(MagnetoService::MAGNETO_SERVICE_UUID, charTable, sizeof(charTable) / sizeof(GattCharacteristic *));
        ble.gattServer().addService(magnetoService);

        serviceAdded = true;
    }

    void updateMagneto(int16_t newMagneto[3]) {
        memset(magneto, '\0', 20);
        sprintf(magneto, "%d,%d,%d;", newMagneto[0], newMagneto[1], newMagneto[2]);
        ble.gattServer().write(magnetoCharacteristic.getValueHandle(), (uint8_t *) magneto, sizeof(magneto));
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
    char magneto[20];
    /*char magnetoY[10];
    char magnetoZ[10];*/
    GattCharacteristic    magnetoCharacteristic;
    /*GattCharacteristic    magnetoYCharacteristic;
    GattCharacteristic    magnetoZCharacteristic;*/
};

#endif 