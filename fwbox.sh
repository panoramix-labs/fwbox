# Copyright (c) 2024 Josuah Demangeon
# SPDX-License-Identifier: MIT

# Collection of shell functions to install to both the local and remote system
# under the path /etc/profile.d/fwbox.sh

FWBOX_OPENOCD=openocd.cfg

# Runners: connect to something that connects to something ...

fwbox_run() {
    # implicit local execution at the end of the chain
    if [ -n "${FWBOX##local *}" ]; then FWBOX="local $FWBOX"; fi
    local list=${FWBOX% *} spec=${FWBOX##* }
    local this=${spec%%,*} opts=$(echo ${spec#*,} | tr ',' ' ')
    echo "fwbox: $*"
    FWBOX=$list fwbox_run_"$this" "$opts" "$@"
}

fwbox_run_local() { local $1; shift
    "$@"
}

fwbox_run_ssh() { local $1; shift
    # Quote every argument
    for x; do set -- "$@" "'$1'"; shift; done
    fwbox_run ssh -p "${port:-22}" "$host" "$*"
}

fwbox_run_picocom() { local $1; shift
    fwbox_run picocom --quiet --exit-after 500 --baud 115200 --initstring "$*$NL" "$port"
    echo
}

# Read a file from standard input and load it into the board

alias fwbox_flash=fwbox_flash_gdb
#1: offset within the flash at which load the firmware
#2: port through which send the flash command

fwbox_flash_gdb() { local port=$2
    fwbox_run gdb-multiarch 
}

fwbox_flash_ecpprog() { local offset=${1:-0x00000000}
    fwbox_run ecpprog -a -o "$offset" -
}

# Send a file to the remote system

alias fwbox_upload=fwbox_upload_scp
#1: address of the remote system onto which upload the file
#2: port of the remote system to connect to
#3: local source file to send to $host
#4: path at which the file will be installed on $host

fwbox_upload_cat() { local dest=$1
    fwbox_run "cat >'$dest'"
}

# Start a GDB server instance

alias fwbox_gdbserver=fwbox_gdbserver_openocd
#1: port to which expose the GDB interface to

fwbox_gdbserver_openocd() { local port=$1
    fwbox_run openocd -f "$FWBOX_OPENOCD" -c "gdb_port :$port"
}

# Connect to a runing GDB server

alias fwbox_gdbclient=fwbox_gdbclient_multiarch
#1: host:port or serial port at which GDB is listening
#2: ELF file to use for symbols

fwbox_gdbclient_multiarch() { local port=$1 file=$2
    fwbox_run gdb-multiarch -q -nx -ex "target extended $port" "$file" -ex "load"
}

# Connect to a serial console for getting the logs or a debug shell

alias fwbox_console=fwbox_console_picocom
#1: serial port device such as /dev/tty# to connect to
#2: serial baud rate for communication

fwbox_console_picocom() { local port=$1 baud=$2
    fwbox_run picocom --quiet --baud "$baud" "$port"
}

# Toggle a GPIO pin to power-cycle a board

alias fwbox_gpioset=fwbox_gpioset_gpiod
#1: GPIO block to control
#2: GPIO pin to control
#3: new state of the GPIO pin (0 or 1)

fwbox_gpioset_gpiod() { local block=$1 pin=$2 val=$3
    fwbox_run gpioset --drive=push-pull "$block" "$pin" "$val"
}

fwbox_gpioset_zephyr() { local block=$1 pin=$2 val=$3
    fwbox_run "$(printf '%s\r' "gpio conf $block $pin o")"
    fwbox_run "$(printf '%s\r' "gpio set $block $pin $val")"
}

fwbox_gpioset_micropython() { local block=$1 pin=$2 val=$3
    fwbox_run "$(printf '\x01%s\x04' "from machine import Pin")"
    fwbox_run "$(printf '\x01%s\x04' "Pin($pin, Pin.OUT).value($val)")"
}

# List GPIO blocks available

alias fwbox_gpioget=fwbox_gpioget_gpiod
#1: port to connect to for controlling the pin
#2: baud rate for that port
#3: GPIO block to control
#4: GPIO pin to control
#5: new state of the GPIO pin (0 or 1)

fwbox_gpioget_gpiod() { local block=$1 pin=$2
    fwbox_run gpioget "$block" "$pin"
}

fwbox_gpioget_zephyr() { local block=$1 pin=$2
    fwbox_run gpio conf "$block" "$pin" i
    fwbox_run gpio get "$block" "$pin"
}
