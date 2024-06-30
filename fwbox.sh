# Copyright (c) 2024 Josuah Demangeon
# SPDX-License-Identifier: MIT

# Collection of shell functions to install to both the local and remote system
# under the path /etc/profile.d/fwbox.sh

FWBOX_OPENOCD=openocd.cfg

# run: run the specified command on the runner according to configuratoin
# $@: command and argument list to execute on the target

fwbox_run() {
    # implicit local execution at the end of the chain
    if [ -n "${FWBOX##local *}" ]; then FWBOX="local $FWBOX"; fi
    local list=${FWBOX% *} spec=${FWBOX##* }
    local this=${spec%%,*} opts=$(echo ${spec#*,} | tr ',' ' ')
    echo "fwbox: $*" | sed 's/\001/^A/g; s/\004/^D/g; s/\r/\\r/g' >&2
    FWBOX=$list fwbox_run_"$this" "$opts" "$@"
}

fwbox_run_local() { local $1; shift
    "$@"
}

fwbox_run_ssh() { local $1; shift
    # Quote every argument
    for x; do set -- "$@" "'$1'"; shift; done
    fwbox_run ssh -Ct -oControlMaster=auto -oControlPath=~/.ssh/%C.sock -p "${port:-22}" "$host" "$*"
}

fwbox_run_picocom() { local $1; shift
    fwbox_run picocom --quiet --exit-after 200 --baud 115200 --initstring "$*" "$port"
}

# flash: read a file from standard input and load it into the board
# $1: offset within the flash at which load the firmware
# $2: port through which send the flash command

fwbox_flash_gdb() { local port=$2
    fwbox_run gdb-multiarch 
}

fwbox_flash_ecpprog() { local offset=${1:-0x00000000}
    fwbox_run ecpprog -a -o "$offset" -
}

# put: send a file to the remote system
# $1: path at which the file will be installed on $host

fwbox_put() { local path=$1
    fwbox_run "cat >'$path'"
}

# gdbserver: start a GDB server instance
# $1: port to which expose the GDB interface to

fwbox_gdbserver_openocd() { local port=$1
    fwbox_run openocd -f "$FWBOX_OPENOCD" -c "gdb_port :$port"
}

# gdbclient: connect to a runing GDB server
# $1: host:port or serial port at which GDB is listening
# $2: ELF file to use for symbols

fwbox_gdbclient_multiarch() { local port=$1 file=$2
    fwbox_run gdb-multiarch -q -nx -ex "target extended $port" "$file" -ex "load"
}

# console: connect to a serial console for getting the logs or a debug shell
# $1: serial port device such as /dev/tty# to connect to
# $2: serial baud rate for communication

fwbox_picocom() { local port=$1 baud=$2
    fwbox_run picocom --quiet --baud "$baud" "$port"
}

# gpioset: toggle a GPIO pin to power-cycle a board
# $1: GPIO block to control
# $2: GPIO pin to control
# $3: new state of the GPIO pin (0 or 1)

fwbox_gpioset_gpiod() { local block=$1 pin=$2 val=$3
    fwbox_run gpioset --drive=push-pull "$block" "$pin" "$val"
}

fwbox_gpioset_zephyr() { local block=$1 pin=$2 val=$3
    fwbox_run "$(printf '\r%s\r%s\r' \
        "gpio conf $block $pin o"\
        "gpio set $block $pin $val")"
}

fwbox_gpioset_micropython() { local block=$1 pin=$2 val=$3
    fwbox_run "$(printf '\x01%s\x04%s\x04' \
        "from machine import Pin" \
        "Pin($pin, Pin.OUT).value($val)")"
}

# gpioget: list GPIO blocks available
# $1: GPIO block to control
# $2: GPIO pin to control

fwbox_gpioget_gpiod() { local block=$1 pin=$2
    fwbox_run gpioget "$block" "$pin"
}

fwbox_gpioget_zephyr() { local block=$1 pin=$2
    fwbox_run gpio conf "$block" "$pin" i
    fwbox_run gpio get "$block" "$pin"
}

# dmesg: clear the dmesg history then watch for new messages

fwbox_dmesg() {
    fwbox_run dmesg -c
    fwbox_run dmesg -w
}
