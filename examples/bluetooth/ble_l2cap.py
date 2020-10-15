import bluetooth
import random
import struct
import time
from ble_advertising import advertising_payload

from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)

_IRQ_L2CAP_ACCEPT = const(22)
_IRQ_L2CAP_CONNECT = const(23)
_IRQ_L2CAP_DISCONNECT = const(24)
_IRQ_L2CAP_RECV = const(25)
_IRQ_L2CAP_TX_UNSTALLED = const(26)

t0 = None
rx = 0
rxbuf = bytearray(1024)
chan_handle = None

class BLEL2CAP:
    def __init__(self, ble, name="mpy-l2cap"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._connections = set()
        self._payload = advertising_payload(
            name=name
        )
        self._advertise()

    def _irq(self, event, data):
        global t0, rx, chan_handle

        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()

        elif event == _IRQ_L2CAP_ACCEPT:
            print('py: l2cap accept', data)

        elif event == _IRQ_L2CAP_CONNECT:
            print('py: l2cap connect', data)
            chan_handle, = data

        elif event == _IRQ_L2CAP_DISCONNECT:
            print('py: l2cap disconnect', data)
            chan_handle = None

        elif event == _IRQ_L2CAP_RECV:
            #print('py: l2cap recv', data)
            chan_handle, = data
            while self._ble.l2cap_recvinto(chan_handle, None):
                n = self._ble.l2cap_recvinto(chan_handle, rxbuf)
                #print('py: rxbuf', n, rxbuf[0:n])
                #print('py: rxbuf', n)
                if t0 is None:
                    t0 = time.ticks_ms()
                rx += n

        elif event == _IRQ_L2CAP_TX_UNSTALLED:
            #print('l2cap unstalled', data)
            pass

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)


def demo():
    ble = bluetooth.BLE()
    temp = BLEL2CAP(ble)

    ble.l2cap_listen(22, 768);

    while True:
        time.sleep_ms(1000)
        if rx:
            msg = 'B/s={} B={}'.format(1000 * rx // time.ticks_diff(time.ticks_ms(), t0), rx)
            print(msg)
            if chan_handle is not None:
                ble.l2cap_send(chan_handle, msg)


if __name__ == "__main__":
    demo()
