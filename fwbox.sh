# Copyright (c) 2024 Josuah Demangeon
# SPDX-License-Identifier: MIT

# Collection of shell functions to install to both the local and remote system
# under the path /etc/profile.d/fwbox.sh

# Default configuration to override in ./.fwbox

FWBOX_OPENOCD=openocd.cfg
FWBOX_TARGET_BAUD=115200
FWBOX_TARGET_PORT=/dev/ttyUSB0

# Runners: execute one more nested step of execution

fwbox_run_dry() { 
    fwbox_runner echo "fwbox: $*"
}

fwbox_run_local() { local host=$1 cmds=$*
    fwbox_runner echo "$cmds"
}

fwbox_run_ssh() { local host=$1 port=$2
    fwbox_runner ssh -p "$port" "$host" "$@"
}

fwbox_run_picocom() { local port=$1 baud=$2; shift 2
    fwbox_runner picocom --quiet --exit-aftrer 0.2 --baudrate 115200 --initstring "$*" "$port"
}

# Read a file from standard input and load it into the board

alias fwbox_flash=fwbox_flash_gdb
#1: offset within the flash at which load the firmware
#2: port through which send the flash command

fwbox_flash_gdb() { local port=$2
    fwbox_cmd gdb-multiarch 
    fwrun_run flash
}

fwbox_flash_ecpprog() { local offset=$1
    fwrun_cmd ecpprog -a -o "$offset" -
    fwrun_run flash
}

# Send a file to the remote system

alias fwbox_upload=fwbox_upload_scp
#1: address of the remote system onto which upload the file
#2: port of the remote system to connect to
#3: local source file to send to $host
#4: path at which the file will be installed on $host

fwbox_upload_cat() { local dest=$1
    fwbox_cmd "cat >'$dest'"
    fwbox_run cat
}

# Start a GDB server instance

alias fwbox_gdbserver=fwbox_gdbserver_openocd
#1: port to which expose the GDB interface to

fwbox_gdbserver_openocd() { local port=$1
    fwbox_cmd openocd -f "$FWBOX_OPENOCD" -c "gdb_port :$port"
    fwbox_run gdbserver
}

# Connect to a runing GDB server

alias fwbox_gdbclient=fwbox_gdbclient_multiarch
#1: host:port or serial port at which GDB is listening
#2: ELF file to use for symbols

fwbox_gdbclient_multiarch() { local port=$1 file=$2
    fwbox_cmd gdb-multiarch -q -nx -ex "target extended $port" "$file" -ex "load"
    fwbox_run gdbclient
}

# Connect to a serial console for getting the logs or a debug shell

alias fwbox_console=fwbox_console_picocom
#1: serial port device such as /dev/tty# to connect to
#2: serial baud rate for communication

fwbox_console_picocom() { local port=$1 baud=$2
    fwbox_cmd picocom --quiet --baud "$baud" "$port"
    fwbox_run console
}

# Toggle a GPIO pin to power-cycle a board

alias fwbox_gpioset=fwbox_gpioset_gpiod
#1: GPIO block to control
#2: GPIO pin to control
#3: new state of the GPIO pin (0 or 1)

fwbox_gpioset_gpiod() { local block=$1 pin=$2 val=$3
    fwbox_cmd gpioset --drive=push-pull "$block" "$pin" "$val"
    fwbox_run gpio
}

fwbox_gpioset_zephyr() { local block=$1 pin=$2 val=$3
    fwbox_cmd "gpio conf $block $pin o"
    fwbox_cmd "gpio set $block $pin $val"
    fwbox_run gpio
}

fwbox_gpioset_micropython() { local block=$1 pin=$2 val=$3
    fwbox_cmd "from machine import Pin"
    fwbox_cmd "Pin($pin, Pin.OUT).value($val)"
    fwbox_run
}

# List GPIO blocks available

alias fwbox_gpiolist=fwbox_gpiolist_gpiod
#1: port to connect to for controlling the pin
#2: baud rate for that port
#3: GPIO block to control
#4: GPIO pin to control
#5: new state of the GPIO pin (0 or 1)

fwbox_gpioget_gpiod() { local block=$1 pin=$2 val=$3
    fwbox_cmd gpioget "$block" "$pin" "$val"
    fwbox_run gpio
}

fwbox_gpioget_zephyr() { local block=$1 pin=$2 val=$3
    fwbox_cmd gpio conf "$block" "$pin" i
    fwbox_cmd gpio get "$block" "$pin" "$val"
    fwbox_run gpio
}
