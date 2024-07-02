# `fwbox`

Collection of shell functions to handle remote development of firmware leveraging
a small board such as a Raspberry PI to SSH into, or any similar hardware.

This script builds-up a command that will program a firmware, toggle a GPIO pin,
start a GDB server like OpenOCD... without requiring extra scripts installed
on the remote server.

It supports multiple hops through serial links and SSH which allows it to run
MicroPython or Zephyr Shell commands so that a small USB devboard can be
connected, leveraging one environment variable to build proxys.

Install fwbox locally:

```
sudo git clone https://github.com/firmware-box/fwbox /opt/fwbox
```

Get all commands sent over SSH:

```bash
FWBOX="ssh,host=172.22.0.2,port=22"
```

Get all commands sent over SSH and then over a serial console:

```bash
FWBOX="ssh,host=172.22.0.2,port=22 picocom,port=/dev/ttyACM0"
```

Set a GPIO pin0.27 to 1 over a serial console after logging to SSH:

```bash
FWBOX="ssh,host=172.22.0.2,port=22 picocom,port=/dev/ttyACM0"
fwbox_zephyr_shell  27 1
```

Board configuration example:

```
. /opt/fwbox/fwbox.sh

box="ssh,host=172.22.0.3,port=22"
dev="picocom,port=/dev/ttyACM0"
log="console,port=/dev/ttyUSB1,baud=153600"

pin_reset="gpio@48000000 0"
pin_power="gpio@48000000 1"

fwbox_do_flash_zephyr() (
    FWBOX="$box"
    fwbox_flash_ecpprog 0x100000 <build/zephyr/zephyr.bin
)

fwbox_do_power_cycle() (
    FWBOX="$box $dev"
    fwbox_gpioset_zephyr $pin_power 0
    fwbox_gpioset_zephyr $pin_power 1
)

fwbox_do_reset() (
    FWBOX="$box $dev"
    fwbox_gpioset_zephyr $pin_reset 0
    fwbox_gpioset_zephyr $pin_reset 1
)

fwbox_do_console() (
    FWBOX="$box $log"
    fwbox_run
)
```
