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

- Read device info chars
- Subscribe to notifications from `a621` and `a625`, and to indications from `a620`

- [s2c] NOTIFY `a621`: `100a 0007 0000 0000 0000 004f`
  - [c2s] ack notify via write to `a622`: `0001 01`
  - [c2s] ack notify via write to `a622`: `0001 01`
- [c2s] WRITE `a624`: `100b 0008 0100 0000 0000 0000 02`
  - [s2c] ack write via notify to `a625`: `0001 01`
- [s2c] NOTIFY `a621`: `1003 0009 18`
  - [c2s] ack notify via write to `a622`: `0001 01`

- [c2s] WRITE `a624`: `1008 000a 1869 ea66 d420`
  - Specifies Unix timestamp as a big-endian int32 in octets 5–9
  - Does not appear to be necessary to operate the scale
  - [s2c] ack write via notify to `a625`: `0001 01`

- [c2s] WRITE `a624`: `1003 1004 02`
  - [s2c] ack write via notify to `a625`: `0001 01`

- [s2c] NOTIFY `a621`: `1005 1000 1004 01`
  - [c2s] ack notify via write to `a622`: `0001 01`

- [c2s] WRITE `a624`: `1009 1002 03d4 66ea 6930`
  - Specifies Unix timestamp as a little-endian int32 in octets 5–9
  - This timestamp appears to be used by the scale, while the `1008` big-endian version appears to
    be ignored/unneeded.
  - [s2c] Ack write via notify to `a625`: `0001 01`

- [s2c] NOTIFY `a621`: `1005 1000 1002 01`
  - [c2s] ack notify via write to `a622`: `0001 01`

- [c2s] WRITE `a624`: `1004 4801 0001`
  - [s2c] ack write via notify to `a625`: `0001 01`

The scale is now ready to send data to the client. If there has already been a weight measurement
prior to the client's connection, it will be sent immediately. Subsequent measurements will be sent
as soon as they stabilize (when the scale beeps) or are locked using the "HOLD" button.

### Weight measurement notifications

The scale sends weight measurement notifications to the same `a621` command/data notification
characteristic. They begin `100e 4802`.

Octets 10–11 are the measured weight in grams, encoded as a big-endian int16.

Octets 12–15 are the Unix timestamp of the measurement, encoded as a big-endian int32.

- [s2c] NOTIFY `a621`: `100e 4802 0000 0000 0008 046f 69ea 66df`
  - 2 lbs 8 oz = 1135 g = 0x046f (big-endian int16)
  - Unix timestamp 1776969439 (2026-04-23 14:37:19) = 0x69ea66df (big-endian int32)
  - [c2s] ack notify via write to `a622`: `0001 01`
- [s2c] NOTIFY `a621`: `100e 4802 0000 0000 0008 066d 69ea 66eb`
  - 3 lbs 10 oz = 1645 g = 0x066d (big-endian int16)
  - Unix timestamp 1776969451 (2026-04-23 14:37:31) = 0x69ea66df (big-endian int32)
  - [c2s] ack notify via write to `a622`: `0001 01`
