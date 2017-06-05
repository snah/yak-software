#! /usr/bin/env python3

import usb

from yak_server import usbdevice

def server_running():
    return True

def main():
    switch_device = usbdevice.find(vendor_id=0x04d8, product_id=0x5900)[0]
    switch_device.connect()

    AC_device = usbdevice.find(vendor_id=0x04d8, product_id=0x5901)[0]
    AC_device.connect()

    while server_running():
        data = switch_device.read(1)

        if data:
            print(data)
            AC_device.write(data)

if __name__ == '__main__':
    main()
