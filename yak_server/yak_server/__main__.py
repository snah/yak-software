import usb

def main():
    switch_device = usb.core.find(idVendor=0x04d8, idProduct=0x5900)
    try:
        switch_device.detach_kernel_driver(0)
    except usb.USBError:
        pass # No kernel driver was attached
    usb.util.claim_interface(switch_device, 0)

    switch_conf = switch_device.get_active_configuration()
    switch_interface = switch_conf.interfaces()[0]
    switch_endpoint = switch_interface.endpoints()[0]

    AC_device = usb.core.find(idVendor=0x04d8, idProduct=0x5901)
    try:
        AC_device.detach_kernel_driver(0)
    except usb.USBError:
        pass # No kernel driver was attached
    usb.util.claim_interface(AC_device, 0)

    AC_conf = AC_device.get_active_configuration()
    AC_interface = AC_conf.interfaces()[0]
    AC_endpoint = AC_interface.endpoints()[0]

    while True:
        try:
            data = switch_endpoint.read(1)
        except usb.USBError:
            continue    # No data received.

        print(data)

        AC_endpoint.write(data)

if __name__ == '__main__':
    main()
