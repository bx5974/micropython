import sys
sys.path.append('')

from micropython import const
import micropython

import bluetooth

import uasyncio as asyncio
import binascii
import io

import ble_advertising

_MP_STREAM_POLL = const(3)

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
_IRQ_GATTS_INDICATE_DONE = const(20)

_ADV_IND = const(0)
_ADV_DIRECT_IND = const(1)
_ADV_SCAN_IND = const(2)
_ADV_NONCONN_IND = const(3)
_SCAN_RSP = const(4)


def log_error(*args):
    print('E:', *args)

def log_info(*args):
    print('I:', *args)


class PollingEvent(io.IOBase):
    def __init__(self):
        self._flag = 0

    def ioctl(self, req, flags):
        if req == _MP_STREAM_POLL:
            return self._flag * flags
        return None

    def set(self):
        self._flag = 1

    async def wait(self):
        yield asyncio.core._io_queue.queue_read(self)
        self._flag = 0


# class Timeout:
#     def __init__(self, timeout_ms):
#         async def timeout():
#             asyncio.sleep_ms(timeout_ms)

#         asyncio.create_task(timeout())

#     async def __aenter__(self):
#         pass

#     async def __aexit__(self, exc_type, exc_val, exc_traceback):
#         pass


ble = bluetooth.BLE()
active_scanner = None
connecting_peripherals = {}
active_connections = {}
registered_characteristics = {}
remote_central = None
remote_central_event = PollingEvent()

def _ensure_active():
    if not ble.active():
        ble.active(True)

async def _cancel_pending():
    if active_scanner:
        await active_scanner.cancel()

def ble_irq(event, data):
    if event == _IRQ_CENTRAL_CONNECT:
        conn_handle, addr_type, addr = data
        Device(addr_type, addr)._central_connected(conn_handle)
    elif event in (_IRQ_CENTRAL_DISCONNECT, _IRQ_PERIPHERAL_DISCONNECT,):
        conn_handle, _, _ = data
        if conn_handle not in active_connections:
            return
        active_connections[conn_handle]._disconnected()
    elif event == _IRQ_GATTS_WRITE:
        conn_handle, attr_handle = data
        Characteristic._remote_write(conn_handle, attr_handle)
    elif event == _IRQ_GATTS_READ_REQUEST:
        conn_handle, attr_handle = data
    elif event == _IRQ_SCAN_RESULT:
        addr_type, addr, adv_type, rssi, adv_data = data
        if not active_scanner:
            return
        active_scanner._queue.append((addr_type, bytes(addr), adv_type, rssi, bytes(adv_data),))
        active_scanner._event.set()
    elif event == _IRQ_SCAN_DONE:
        if not active_scanner:
            return
        active_scanner._done = True
        active_scanner._event.set()
    elif event == _IRQ_PERIPHERAL_CONNECT:
        conn_handle, addr_type, addr = data
        d = Device(addr_type, addr)
        if d not in connecting_peripherals:
            return
        connecting_peripherals[d]._peripheral_connected(conn_handle)
    elif event == _IRQ_GATTC_SERVICE_RESULT:
        conn_handle, start_handle, end_handle, uuid = data
        ClientDiscover._result(conn_handle, start_handle, end_handle, bluetooth.UUID(uuid))
    elif event == _IRQ_GATTC_SERVICE_DONE:
        conn_handle, status = data
        ClientDiscover._done(conn_handle, status)
    elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
        conn_handle, def_handle, value_handle, properties, uuid = data
        ClientDiscover._result(conn_handle, def_handle, value_handle, properties, bluetooth.UUID(uuid))
    elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
        conn_handle, status = data
        ClientDiscover._done(conn_handle, status)
    elif event == _IRQ_GATTC_DESCRIPTOR_RESULT:
        conn_handle, dsc_handle, uuid = data
        ClientDiscover._result(conn_handle, dsc_handle, bluetooth.UUID(uuid))
    elif event == _IRQ_GATTC_DESCRIPTOR_DONE:
        conn_handle, status = data
        ClientDiscover._done(conn_handle, status)
    elif event == _IRQ_GATTC_READ_RESULT:
        conn_handle, value_handle, char_data = data
        ClientCharacteristic._read_result(conn_handle, value_handle, char_data)
    elif event in (_IRQ_GATTC_READ_DONE, _IRQ_GATTC_WRITE_DONE,):
        conn_handle, value_handle, status = data
        ClientCharacteristic._done(conn_handle, value_handle, status)
    elif event == _IRQ_GATTC_NOTIFY:
        conn_handle, value_handle, notify_data = data
    elif event == _IRQ_GATTC_INDICATE:
        conn_handle, value_handle, notify_data = data
    elif event == _IRQ_GATTS_INDICATE_DONE:
        conn_handle, value_handle, status = data
        Characteristic._indicate_done(conn_handle, value_handle, status)

ble.irq(ble_irq)

class ClientService:
    def __init__(self, device, start_handle, end_handle, uuid):
        self._device = device
        self._start_handle = start_handle
        self._end_handle = end_handle
        self._uuid = uuid

    def __str__(self):
        return 'Service: {} {} {}'.format(self._start_handle, self._end_handle, self._uuid)

    async def characteristic(self, uuid):
        result = None
        # Make sure loop runs to completion.
        async for characteristic in self.characteristics(uuid):
            result = characteristic
        return result

    def characteristics(self, uuid):
        return ClientDiscover(self._device, ClientCharacteristic, self, uuid)

    @staticmethod
    def _start(device, uuid=None):
        ble.gattc_discover_services(device._conn_handle, uuid)

class ClientCharacteristic:
    def __init__(self, service, def_handle, value_handle, properties, uuid):
        self._service = service
        self._def_handle = def_handle
        self._value_handle = value_handle
        self._properties = properties
        self._uuid = uuid
        self._event = PollingEvent()
        self._data = None
        self._status = None

    def __str__(self):
        return 'Characteristic: {} {} {} {}'.format(self._def_handle, self._value_handle, self._properties, self._uuid)

    @staticmethod
    def _start(service, uuid=None):
        ble.gattc_discover_characteristics(service._device._conn_handle, service._start_handle, service._end_handle, uuid)

    async def read(self):
        self._service._device._pending_characteristics[self._value_handle] = self
        self._status = None
        ble.gattc_read(self._service._device._conn_handle, self._value_handle)
        while self._status is None:
            await self._event.wait()
        return self._data

    async def write(self, response=False):
        pass

    @staticmethod
    def _get_characteristic(conn_handle, value_handle):
        if conn_handle not in active_connections:
            return None
        device = active_connections[conn_handle]
        if value_handle not in device._pending_characteristics:
            if value_handle == 0xffff and len(device._pending_characteristics) == 1:
                # Workaround for btstack which doesn't give us value handle for the done event.
                # Assume only one pending characteristic.
                return next(iter(device._pending_characteristics.values()))
            return None
        return device._pending_characteristics[value_handle]

    @staticmethod
    def _read_result(conn_handle, value_handle, data):
        characteristic = ClientCharacteristic._get_characteristic(conn_handle, value_handle)
        if not characteristic:
            return
        characteristic._data = data
        characteristic._event.set()

    def _done(conn_handle, value_handle, status):
        characteristic = ClientCharacteristic._get_characteristic(conn_handle, value_handle)
        if not characteristic:
            return
        characteristic._status = status
        characteristic._event.set()
        del characteristic._service._device._pending_characteristics[characteristic._value_handle]

class ClientDiscover:
    def __init__(self, device, disc_type, parent, *args):
        self._device = device
        self._queue = []
        self._event = PollingEvent()
        self._status = None
        self._disc_type = disc_type
        self._parent = parent
        self._args = args

    async def _start(self):
        # TODO: cancel existing
        self._device._discover = self
        self._disc_type._start(self._parent, *self._args)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._device._discover != self:
            await self._start()

        while True:
            if self._queue:
                return self._disc_type(self._parent, *self._queue.pop())
            if self._status is not None:
                self._device._discover = None
                raise StopAsyncIteration
            await self._event.wait()

    @staticmethod
    def _result(conn_handle, *args):
        if conn_handle not in active_connections:
            return
        discover = active_connections[conn_handle]._discover
        if not discover:
            return
        discover._queue.append(args)
        discover._event.set()

    def _done(conn_handle, status):
        if conn_handle not in active_connections:
            return
        discover = active_connections[conn_handle]._discover
        if not discover:
            return
        discover._status = status
        discover._event.set()


class Device:
    def __init__(self, addr_type, addr):
        self.addr_type = addr_type
        self.addr = addr

        self._conn_handle = None
        self._event = PollingEvent()

        self._discover = None
        self._pending_characteristics = {}

    def __eq__(self, rhs):
        return self.addr_type == rhs.addr_type and self.addr == rhs.addr

    def __hash__(self):
        return hash((self.addr_type, self.addr))

    def __str__(self):
        return 'Device({},{}{})'.format(self.addr_type, binascii.hexlify(self.addr), ',{}'.format(self._conn_handle) if self._conn_handle else '')

    async def connect(self):
        _ensure_active()
        await _cancel_pending()
        connecting_peripherals[self] = self
        ble.gap_connect(self.addr_type, self.addr)
        await self._event.wait()

    def _peripheral_connected(self, conn_handle):
        self._conn_handle = conn_handle
        del connecting_peripherals[self]
        active_connections[conn_handle] = self
        self._event.set()

    def _central_connected(self, conn_handle):
        self._conn_handle = conn_handle
        active_connections[conn_handle] = self
        global remote_central
        remote_central = self
        remote_central_event.set()

    async def disconnect(self):
        if self._conn_handle is not None:
            ble.gap_disconnect(self._conn_handle)
            self._conn_handle = None
            await self._event.wait()

    def _disconnected(self):
        del active_connections[self._conn_handle]
        self._conn_handle = None
        self._event.set()

    async def service(self, uuid):
        result = None
        # Make sure loop runs to completion.
        async for service in self.services(uuid):
            result = service
        return result

    def services(self, uuid=None):
        return ClientDiscover(self, ClientService, self, uuid)

    def is_connected(self):
        return self._conn_handle is not None

class ScanResult:
    def __init__(self, device):
        self.device = device
        self.adv_data = None
        self.scan_resp = None
        self.rssi = None
        self.connectable = False

    def _update(self, adv_type, rssi, adv_data):
        self.rssi = rssi

        updated = False

        if adv_type in (_ADV_IND, _ADV_NONCONN_IND,):
            if adv_data != self.adv_data:
                self.adv_data = adv_data
                self.connectable = adv_type == _ADV_IND
                updated = True
        elif adv_type == _ADV_SCAN_IND:
            if adv_data != self.adv_data and self.scan_resp:
                updated = True
            self.adv_data = adv_data
        elif adv_type == _SCAN_RSP and adv_data:
            if adv_data != self.scan_resp:
                self.scan_resp = adv_data
                updated = True

        return updated

    def __str__(self):
        return 'Scan result: {} {} {} {}'.format(self.device, self.rssi, self.adv_data, self.scan_resp)

    def name(self):
        return ble_advertising.decode_name(self.adv_data)

class scan:
    def __init__(self, duration_ms, interval_us=None, window_us=None, active=None):
        self._queue = []
        self._event = PollingEvent()
        self._done = False
        self._results = {}
        self._duration_ms = duration_ms

    async def _start(self):
        _ensure_active()
        await _cancel_pending()
        global active_scanner
        active_scanner = self
        ble.gap_scan(self._duration_ms, 30000, 30000, True)

    def __aiter__(self):
        return self

    async def __anext__(self):
        global active_scanner
        if active_scanner != self:
            await self._start()

        while True:
            if self._queue:
                addr_type, addr, adv_type, rssi, adv_data = self._queue.pop()
                device = Device(addr_type, addr)
                if device not in self._results:
                    self._results[device] = ScanResult(device)
                if self._results[device]._update(adv_type, rssi, adv_data):
                    return self._results[device]
            if self._done:
                active_scanner = None
                raise StopAsyncIteration
            await self._event.wait()

    # TODO: need __aiterclose__ to do this automatically
    # Right now we do this before starting any other operation.
    async def cancel(self):
        if self._done:
            return
        log_info('Cancelling active scan.')
        ble.gap_scan(None)
        while not self._done:
            await self._event.wait()
        global active_scanner
        active_scanner = None

class Service:
    def __init__(self, uuid):
        self.uuid = uuid
        self.characteristics = []

    def _tuple(self):
        return (self.uuid, tuple(c._tuple() for c in self.characteristics))

class Characteristic:
    def __init__(self, service, uuid, flags):
        service.characteristics.append(self)
        self.descriptors = []
        self._init(uuid, flags)

    def _init(self, uuid, flags):
        self.uuid = uuid
        self.flags = flags
        self._value_handle = None

        if flags & bluetooth.FLAG_WRITE:
            self._receive_event = PollingEvent()

        if flags & bluetooth.FLAG_INDICATE:
            # TODO: This should probably be a dict of device to (ev, status).
            self._indicate_device = None
            self._indicate_event = PollingEvent()
            self._indicate_status = None

    def _register(self, value_handle):
        self._value_handle = value_handle
        registered_characteristics[value_handle] = self

    def _tuple(self):
        return (self.uuid, self.flags)

    def read(self):
        return ble.gatts_read(self._value_handle)

    def write(self, data):
        ble.gatts_write(self._value_handle, data)

    def notify(self, device, data=None):
        if not (self.flags & bluetooth.FLAG_NOTIFY):
            raise ValueError()
        ble.gatts_notify(device._conn_handle, self._value_handle, data)

    async def indicate(self, device):
        if not (self.flags & bluetooth.FLAG_INDICATE):
            raise ValueError()
        if self._indicate_device is not None:
            raise ValueError()
        if not device.is_connected():
            raise ValueError()

        self._indicate_device = device
        self._indicate_status = None
        ble.gatts_indicate(device._conn_handle, self._value_handle)
        await self._indicate_event.wait()
        return self._indicate_status

    async def receive(self):
        if not (self.flags & bluetooth.FLAG_INDICATE):
            raise ValueError()
        await self._receive_event.wait()

    @staticmethod
    def _remote_write(conn_handle, value_handle):
        if value_handle not in registered_characteristics:
            return
        characteristic = registered_characteristics[value_handle]
        characteristic._receive_event.set()

    @staticmethod
    def _indicate_done(conn_handle, value_handle, status):
        if value_handle not in registered_characteristics:
            return
        characteristic = registered_characteristics[value_handle]
        if characteristic._indicate_device._conn_handle != conn_handle:
            return
        characteristic._indicate_status = status
        characteristic._indicate_device = None
        characteristic._indicate_event.set()


class BufferedCharacteristic(Characteristic):
    def __init__(self, service, uuid, flags, max_len=20, append=False):
        super().__init__(service, uuid, flags)
        self._max_len = max_len
        self._append = append

    def _register(self, value_handle):
        super()._register(value_handle)
        ble.gatts_set_buffer(value_handle, self._max_len, self._append)


class Descriptor(Characteristic):
    def __init__(self, characteristic, uuid, flags):
        characteristic.descriptors.append(self)
        self._init(uuid, flags)


def register_services(*services):
    _ensure_active()
    registered_characteristics.clear()
    handles = ble.gatts_register_services(tuple(s._tuple() for s in services))
    for i in range(len(services)):
        service_handles = handles[i]
        service = services[i]
        n = 0
        for characteristic in service.characteristics:
            characteristic._register(service_handles[n])
            n += 1
            for descriptor in characteristic.descriptors:
                descriptor._register(service_handles[n])
                n += 1


async def advertise(interval_us, adv_data=None, resp_data=None, connectable=True):
    global remote_central
    _ensure_active()
    ble.gap_advertise(interval_us, adv_data, resp_data=resp_data, connectable=connectable)
    await remote_central_event.wait()
    result = remote_central
    remote_central = None
    return result
