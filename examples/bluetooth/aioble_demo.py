import sys
sys.path.append('')

import uasyncio as asyncio
import aioble

import bluetooth
import ble_advertising

from micropython import const

import random
import struct

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

def encode_temperature(temp_deg_c):
    return struct.pack("<h", int(temp_deg_c * 100))

def decode_temperature(data):
    return struct.unpack("<h", data)[0] / 100

async def central():
    d = None
    async for result in aioble.scan(5000):
        if result.name() == 'mpy-temp':
            d = result.device
            break

    if d:
        await d.connect()

        temp_service = await d.service(_ENV_SENSE_UUID)

        if temp_service:
            temp_characteristic = await temp_service.characteristic(_ENV_SENSE_TEMP_UUID)

            if temp_characteristic:
                print(decode_temperature(await temp_characteristic.read()))

        await d.disconnect()

remote_device = None

async def peripheral_listen():
    global remote_device
    while True:
        payload = ble_advertising.advertising_payload(
            name='mpy-temp', services=[_ENV_SENSE_UUID], appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER
        )
        device = await aioble.advertise(250000, payload)
        remote_device = device
        print('Connection from', device)


async def peripheral():
    temp_service = aioble.Service(_ENV_SENSE_UUID)
    temp_characteristic = aioble.Characteristic(temp_service, _ENV_SENSE_TEMP_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_WRITE | bluetooth.FLAG_NOTIFY | bluetooth.FLAG_INDICATE)
    aioble.register_services(temp_service)

    asyncio.create_task(peripheral_listen())

    i = 0
    t = 22.5
    while True:
        temp_characteristic.write(encode_temperature(t))
        if i % 10 == 0 and remote_device and remote_device.is_connected():
            temp_characteristic.notify(remote_device)
        t += random.uniform(-0.5, 0.5)
        i += 1
        await asyncio.sleep_ms(500)

#asyncio.run(central())
asyncio.run(peripheral())
