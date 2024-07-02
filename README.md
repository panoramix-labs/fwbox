# `fwbox`

Collection of shell functions to handle remote development of firmware leveraging
a small board such as a Raspberry PI to SSH into, or any similar hardware.

This script builds-up a command that will program a firmware, toggle a GPIO pin,
start a GDB server like OpenOCD... without requiring extra scripts installed
on the remote server.

It supports multiple hops through serial links and SSH which allows it to run
MicroPython or Zephyr Shell commands so that a small USB devboard can be
connected, leveraging one environment variable to build proxys.

Get started:

```
# Install fwbox
sudo git clone https://github.com/firmware-box/fwbox /opt/fwbox

# Source fwbox.sh to have the `fwbox_use` utility at hand
. /opt/fwbox/fwbox.sh

# Load the .fwbox/tinyclunx33_sita.sh script
fwbox_use tinyclunx33_sita

# Run any command from this list
fwbox_do_<TAB>

# Or connect to the development box to run custom commands
fwbox_run
```

Send commands over SSH:

```bash
FWBOX="ssh,host=172.22.0.2,port=22"
```

Send commands over SSH then picocom, to set a GPIO pin

```bash
FWBOX="ssh,host=172.22.0.2,port=22 picocom,port=/dev/ttyACM0"
fwbox_zephyr_shell gpio@48000000 27 1
```

Board configuration example:

```bash
. /opt/fwbox/fwbox.sh

# Description of how to connect to various resources
FWBOX="ssh,host=172.22.0.3,port=22"
FWBOX_GPIO="$FWBOX picocom,port=/dev/ttyACM0 repl"
FWBOX_LOGS="$FWBOX console,port=/dev/ttyUSB1,baud=153600"

# Configuration for built-in actions
FWBOX_GPIO_RESET="gpio@48000000 0"
FWBOX_GPIO_POWER="gpio@48000000 1"

# Alias to choose the syntax for built-in actions
alias fwbox_gpioset=fwbox_gpioset_zephyr

fwbox_do_flash_zephyr() {
    fwbox_flash 0x100000 <build/zephyr/zephyr.bin
}

fwbox_do_all() {
    fwbox_do_flash_zephyr
    fwbox_do_power_cycle
    fwbox_do_reset
}
```

Built-in actions:

- `fwbox_do_power_cycle` - issue a power cycle by toggling GPIO pins
- `fwbox_do_reset` - issue a soft reset by toggling GPIO pins
- `fwbox_do_dmesg` - access to the dmesg kernel debug messages feed
- `fwbox_do_logs` - access to the logs from the device over serial
