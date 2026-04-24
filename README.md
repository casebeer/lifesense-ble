# Greater Goods 0220/Transtek BS-1711 BLE baby scale client

Bluetooth baby scale sold under the brands:

- Greater Goods 0220
- Transtek BS-1711
- Lifesense 智能体重秤

Possibly related to:

- Rotamed Baby Scale BS-1711

## GATT services and characteristics

The primary service on the device is `0000a602-0000-1000-8000-00805f9b34fb`.

The scale sends data and commands to the client as notifications to the characteristic `a621`. These
must be acknowledged manually by the client via write-without-response to the characteristic `a622`.

The client sends commands to the scale via write-without-response to the characteristic `a624`. The
scale will acknowledge these writes via notify to the characteristic `a625`.

    [Service] 0000180a-0000-1000-8000-00805f9b34fb: Device Information
      [Characteristic] 00002a29-0000-1000-8000-00805f9b34fb: (read)
      [Characteristic] 00002a24-0000-1000-8000-00805f9b34fb: (read)
      [Characteristic] 00002a25-0000-1000-8000-00805f9b34fb: (read)
      [Characteristic] 00002a27-0000-1000-8000-00805f9b34fb: (read)
      [Characteristic] 00002a26-0000-1000-8000-00805f9b34fb: (read)
      [Characteristic] 00002a28-0000-1000-8000-00805f9b34fb: (read)

    [Service] 0000a602-0000-1000-8000-00805f9b34fb: Vendor specific
      [Characteristic] 0000a620-0000-1000-8000-00805f9b34fb: (indicate,read)
      [Characteristic] 0000a621-0000-1000-8000-00805f9b34fb: (notify,read)
      [Characteristic] 0000a622-0000-1000-8000-00805f9b34fb: (write-without-response)
      [Characteristic] 0000a623-0000-1000-8000-00805f9b34fb: (write)
      [Characteristic] 0000a624-0000-1000-8000-00805f9b34fb: (write-without-response)
      [Characteristic] 0000a625-0000-1000-8000-00805f9b34fb: (notify,read)
      [Characteristic] 0000a640-0000-1000-8000-00805f9b34fb: (read)
      [Characteristic] 0000a641-0000-1000-8000-00805f9b34fb: (read)

    [Service] 00001530-1212-efde-1523-785feabcd123: Device Firmware Update Service
      [Characteristic] 00001531-1212-efde-1523-785feabcd123: (write,notify)
      [Characteristic] 00001532-1212-efde-1523-785feabcd123: (write-without-response)
      [Characteristic] 00001534-1212-efde-1523-785feabcd123: (read)

## Example GATT transaction

TODO
