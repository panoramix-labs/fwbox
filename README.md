# `fwbox`

Collection of shell functions to handle remote development of firmware leveraging
a small board such as a Raspberry PI to SSH into, or any similar hardware.

This script builds-up a command that will program a firmware, toggle a GPIO pin,
start a GDB server like OpenOCD... without requiring extra scripts installed
on the remote server.

It supports multiple hops through serial links and SSH which allows it to run
MicroPython or Zephyr Shell commands so that a small USB devboard can be
connected, leveraging one environment variable to build proxys.

Get all commands sent over SSH:

```bash
FWBOX="ssh,host=172.22.0.2,port=22"
```

Get all commands sent over SSH and then over a serial console:

```bash
FWBOX="ssh,host=172.22.0.2,port=22 picocom,port=/dev/ttyACM0"
```

Run the default GDB server on port `:3333`

```bash
fwbox_gdbserver :3333
```

Use a connection method just to set a GPIO pin0.27 to 1:

```bash
FWBOX="ssh,host=172.22.0.2,port=22 picocom,port=/dev/ttyACM0" \
fwbox_gpioset gpiochip0 27 1
```

Script example:

```bash
. /opt/fwbox/fwbox.sh

FWBOX="ssh,host=172.22.0.3,port=22"
fwbox_flash_ecpprog 0x100000 <build/zephyr/zephyr.bin

FWBOX="ssh,host=172.22.0.3,port=22 picocom,port=/dev/ttyACM0"
fwbox_gpioset_zephyr gpio@48000000 1 0
fwbox_gpioset_zephyr gpio@48000000 1 1
```

Configuration example:
```bash
. /opt/fwbox/fwbox.sh

FWBOX="ssh,host=172.22.0.3,port=22"
FWBOX_PIN_POWER="gpio@48000000 0"
FWBOX_PIN_RESET="gpio@48000000 1"

alias fwbox_gpioset=fwbox_gpioset_zephyr

fwbox_do_power_cycle() (
    FWBOX="$FWBOX picocom,port=/dev/ttyACM0"
    fwbox_gpioset $FWBOX_PIN_POWER 0
    fwbox_gpioset $FWBOX_PIN_POWER 1
)

fwbox_do_reset() (
    FWBOX="$FWBOX picocom,port=/dev/ttyACM0"
    fwbox_gpioset $FWBOX_PIN_RESET 0
    fwbox_gpioset $FWBOX_PIN_RESET 1
)

fwbox_do_console() (
    fwbox_picocom /dev/ttyUSB1 196000
)
```
