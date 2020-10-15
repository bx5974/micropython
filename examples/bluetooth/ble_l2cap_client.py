# This example finds and connects to a BLE temperature sensor (e.g. the one in ble_temperature.py).

import bluetooth
import random
import struct
import time
import micropython

from ble_advertising import decode_services, decode_name

from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)

_IRQ_L2CAP_ACCEPT = const(22)
_IRQ_L2CAP_CONNECT = const(23)
_IRQ_L2CAP_DISCONNECT = const(24)
_IRQ_L2CAP_RECV = const(25)
_IRQ_L2CAP_TX_UNSTALLED = const(26)

device_addr = None
conn_handle = None
chan_handle = None
stalled = False
ble = None

rxbuf = bytearray(1024)

def _ble_irq(event, data):
    global device_addr, conn_handle, chan_handle, stalled

    if event == _IRQ_SCAN_RESULT:
        addr_type, addr, adv_type, rssi, adv_data = data
        if decode_name(adv_data) == 'mpy-l2cap':
            device_addr = addr_type, bytes(addr)
            ble.gap_scan(None)

    if event == _IRQ_PERIPHERAL_CONNECT:
        conn_handle, addr_type, addr = data

    if event == _IRQ_L2CAP_ACCEPT:
        print('l2cap accept', data)

    if event == _IRQ_L2CAP_CONNECT:
        print('l2cap connect', data)
        chan_handle, = data

    if event == _IRQ_L2CAP_DISCONNECT:
        print('l2cap disconnect', data)

    if event == _IRQ_L2CAP_RECV:
        n = ble.l2cap_recvinto(chan_handle, rxbuf)
        print(rxbuf[0:n])

    if event == _IRQ_L2CAP_TX_UNSTALLED:
        #print('l2cap unstalled', data)
        stalled = False


def demo():
    global ble, stalled
    ble = bluetooth.BLE()
    ble.active(True)
    ble.irq(_ble_irq)

    ble.gap_scan(2000, 30000, 30000)

    for i in range(20):
        if device_addr:
            break
        time.sleep_ms(100)
    else:
        print('No device found')
        return

    print('Connect to', device_addr)
    ble.gap_connect(*device_addr)

    for i in range(20):
        if conn_handle is not None:
            break
        time.sleep_ms(100)
    else:
        print('No connection')
        return

    print('Connected')

    ble.l2cap_connect(conn_handle, 22, 768)

    for i in range(20):
        if chan_handle is not None:
            break
        time.sleep_ms(100)
    else:
        print('No l2cap connection')
        return

    i = 0
    n = 0

    data = bytes(range(256)) + bytes(range(256))
    while n < 20:
        if not stalled:
            stalled = ble.l2cap_send(chan_handle, data)
        #print(stalled)
        #time.sleep_ms(100)

    time.sleep_ms(500)
    ble.l2cap_disconnect(chan_handle)
    ble.gap_disconnect(conn_handle)


if __name__ == "__main__":
    demo()
