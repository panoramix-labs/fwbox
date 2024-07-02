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

Sent commands over SSH:

```bash
FWBOX="ssh,host=172.22.0.2,port=22"
```

Log into SSH, then into picocom, then set a GPIO pin

```bash
FWBOX="ssh,host=172.22.0.2,port=22 picocom,port=/dev/ttyACM0"
fwbox_zephyr_shell  27 1
```

Board configuration example:

```bash
. /opt/fwbox/fwbox.sh

# Description of how to connect to various resources
FWBOX="ssh,host=172.22.0.3,port=22"
FWBOX_GPIO="$FWBOX picocom,port=/dev/ttyACM0 zephyr"
FWBOX_LOGS="$FWBOX console,port=/dev/ttyUSB1,baud=153600"

# Configuration for built-in actions
FWBOX_GPIO_RESET="gpio@48000000 0"
FWBOX_GPIO_POWER="gpio@48000000 1"

# Command alias to choose the syntax for built-in actions
alias fwbox_gpioset=fwbox_gpioset_zephyr

fwbox_do_flash_zephyr() {
    fwbox_flash 0x100000 <build/zephyr/zephyr.bin
}
```

Built-in actions:

- `fwbox_do_power_cycle` - issue a power cycle by toggling GPIO pins
- `fwbox_do_reset` - issue a soft reset by toggling GPIO pins
- `fwbox_do_dmesg` - access to the dmesg kernel debug messages feed
- `fwbox_do_logs` - access to the logs from the device over serial
