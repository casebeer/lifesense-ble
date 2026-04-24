'''
Read weights from Greater Goods 0220 baby scale.
'''
import asyncio
from bleak import BleakClient, BleakScanner
import bleak
import time
import struct
from dataclasses import dataclass
import datetime

import logging
logger = logging.getLogger(__name__)


'''
[Service] 0000a602-0000-1000-8000-00805f9b34fb: Vendor specific
  [Characteristic] 0x16 0000a620-0000-1000-8000-00805f9b34fb: (indicate,read)
  [Characteristic] 0x19 0000a621-0000-1000-8000-00805f9b34fb: (read,notify)
  [Characteristic] 0x1c 0000a622-0000-1000-8000-00805f9b34fb: (write-without-response)
  [Characteristic] 0x1e 0000a623-0000-1000-8000-00805f9b34fb: (write)
  [Characteristic] 0x20 0000a624-0000-1000-8000-00805f9b34fb: (write-without-response)
  [Characteristic] 0x22 0000a625-0000-1000-8000-00805f9b34fb: (read,notify)
  [Characteristic] 0x25 0000a640-0000-1000-8000-00805f9b34fb: (read)
  [Characteristic] 0x27 0000a641-0000-1000-8000-00805f9b34fb: (read)
'''

ggService = '0000a602-0000-1000-8000-00805f9b34fb'

# scale implements (mandatory) "manual" acks of writes and notifies
# when the scale server notifies us on the s2c command char a621, we must write-without-response to
# the notify ack char a622.
char21 = ggChar1 = '0000a621-0000-1000-8000-00805f9b34fb' # notify s2c commands
char22 = '0000a622-0000-1000-8000-00805f9b34fb' # write c2s ack notifies

# when we write to the server on c2s command char a624, the scale will ack via notify to char a625
char24 = '0000a624-0000-1000-8000-00805f9b34fb' # write c2s commands
char25 = ggChar5 = '0000a625-0000-1000-8000-00805f9b34fb' # notify s2c ack writes


# Unknown/unused
char20 = ggChar0 = '0000a620-0000-1000-8000-00805f9b34fb' # indicate
char23 = '0000a623-0000-1000-8000-00805f9b34fb'
char26 = '0000a626-0000-1000-8000-00805f9b34fb'

char40 = ggChar40 = '0000a640-0000-1000-8000-00805f9b34fb'
char41 = ggChar41 = '0000a641-0000-1000-8000-00805f9b34fb'

async def main():
    logging.basicConfig(level=logging.INFO)

    serviceUuids = [bleak.uuids.normalize_uuid_str(u) for u in [ggService]]
    async with BleakScanner(service_uuids=serviceUuids) as scanner:
        async for device, ad in scanner.advertisement_data():
            print(device)
            break

    async with BleakClient(device) as client:
        print(f"Connected: {client.is_connected}")

        # Iterate through all services discovered on the device
        for service in client.services:
            print(f"\n[Service] {service.uuid}: {service.description}")

            # Optionally print characteristics for each service
            for char in service.characteristics:
                print(f"  [Characteristic] 0x{char.handle:x} {char.uuid}: ({','.join(char.properties)})")

        service = client.services.get_service(ggService)
        #for c in [ggChar0, ggChar1, ggChar5]:
        #    char = service.get_characteristic(c)
        #    await client.start_notify(char, callback)
        #    logger.info(f"Subscribed to {char}")
        #

        writeAckEvent = asyncio.Event()

        async def writeAck():
            await writeAckEvent.wait()
            writeAckEvent.clear()

        async def ackNotify():
            await client.write_gatt_char(char22, bytes.fromhex("000101"), response=False)
            print(">  ack_notify")

        async def writeValue(value: bytes):
            await client.write_gatt_char(char24, value, response=False)
            print(f">  write {value.hex()}")
            await writeAck()


        async def handle_command(char, data):
            command = data[0:4].hex()
            timestamp = int(time.time())

            if char.uuid.lower() == char25.lower():
                print(" < write_ack")
                writeAckEvent.set()
            elif char.uuid.lower() == char21.lower():
                print(f" < data_notify {data.hex()}")
                await ackNotify()
            else:
                print(f"NOTIFY: {char}: {data.hex()}")


            # only on char21
            match data.hex():
                #     # could last byte be battery percentage? went from 4f=79 to 47=71
                #      100a00070000000000000047
                #case "100a0007000000000000004f":
                case s if s.startswith("100a0007"):
                                                #   100b 0008 0100 0000 0000 0000 02
                    await writeValue(bytes.fromhex("100b0008010000000000000002"))

                #     1003 0009 18
                case "1003000918":
                    #await asyncio.sleep(.1)
                    #print("writing 1008 big-endian time")
                    #                                          # 1008 000a 18
                    #value = struct.pack(">5sls", bytes.fromhex("1008000a18"), timestamp, b"\x20")
                    #print(value.hex())
                    #await client.write_gatt_char(char24, value, response=False)
                    #await asyncio.sleep(.1)
                                                  # 1003 1004 02
                    await writeValue(bytes.fromhex("1003100402"))

                    # 1005 1000 1004 01
                case "10051000100401":
                    #await asyncio.sleep(.1)
                    print("writing 1009 little-endian time")
                    value = struct.pack("<5sls", bytes.fromhex("1009100203"), timestamp, b"\x30")
                    #print(value.hex())
                    #print(timestamp)
                    #print(struct.pack("<l", timestamp).hex())
                    await writeValue(value)

                    # 1005 1000 1002 01
                case "10051000100201":
                                                  # 1004 4801 0001
                    await writeValue(bytes.fromhex("100448010001"))
                    print("Waiting for data...")

                                      # 100e 4802
                case s if s.startswith("100e4802"):
                    print(parse_measurement(data))
                    print("Waiting for data...")

                    # 1003 2004 00
                case "1003200400":
                    print("Scale set to kg")
                case "1003200401":
                    print("Scale set to lbs")
                case "1003200402":
                    print("Scale set to lbs + oz")




        async def callback(char, data: bytearray):
            #print(f"NOTIFY: {char}: {data.hex()}")
            await handle_command(char, data)



        for char in service.characteristics:
            if "notify" in char.properties or "indicate" in char.properties:
                await client.start_notify(char, callback)

        #await asyncio.sleep(5)

        #for char in [ggChar1, ggChar5, ggChar40, ggChar41]:
        #    data = await client.read_gatt_char(char)
        #    print(f"read {char} = {data.hex()}")

        await asyncio.Event().wait()

def parse_measurement(data):
    # 100e 4802 0000 0000 0008 0538 69eafdcc
    # 100e 4802 0000 0000 0008 0537 69ea66df
    _, _, _, _, _, grams, timestamp = struct.unpack(">hhhhhhl", data)
    return Measurement(grams=grams, timestamp=datetime.datetime.fromtimestamp(timestamp))

@dataclass
class Measurement:
    grams: int
    timestamp: datetime.datetime

'''
  - NOTIFY a621:         100a 0007 0000 0000 0000 004f
  - WRITE handle 0x001d 000101
  - WRITE handle 0x001d 000101
  - WRITE handle 0x0021: 100b 0008 0100 0000 0000 0000 02

- NOTIFY a625 0001 01

- NOTIFY a621 1003 0009 18
- WRITE handle 0x001d 0001 01

- WRITE handle 0x0021 1008 000a 1869 ea66 d420
- NOTIFY a625 0001 01

- WRITE handle 0x0021 1003 1004 02
- NOTIFY a625 0001 01

- NOTIFY a621 1005 1000 1004 01
- WRITE handle 0x001d 0001 01

- WRITE handle 0x0021 1009 1002 03d4 66ea 6930
- NOTIFY a625 0001 01

- NOTIFY a621 1005 1000 1002 01
- WRITE handle 0x001d 0001 01

- WRITE handle 0x0021 1004 4801 0001
- NOTIFY a625 0001 01
'''

# Run the asynchronous event loop
asyncio.run(main())
