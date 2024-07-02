# Copyright (c) 2024 Josuah Demangeon
# SPDX-License-Identifier: MIT

# Collection of shell functions to install only on the local system
# under the path /opt/fwbox/fwbox.sh

GDB=gdb-multiarch
SSH=ssh
PICOCOM=picocom
ECPPROG=ecpprog

# runner: send the specified command on the runner according to the chain in $FWBOX
# $@: command and argument list to execute on the target
# $FWBOX: specification telling where the command should be run

fwbox_run() {
    if [ -n "${FWBOX##local *}" ]; then FWBOX="local $FWBOX"; fi
    echo "fwbox: $*" | cat -v >&2
    FWBOX=${FWBOX% *} fwbox_runner_$(echo ${FWBOX##* } | tr ',' ' ') "$@"
}

fwbox_runner_local() { local $1; shift
    "$@"
}

fwbox_runner_ssh() { local $1; shift
    for x; do set -- "$@" "'$1'"; shift; done
    fwbox_run $SSH -Ct -oControlMaster=auto -oControlPath=~/.ssh/%C.sock -p "${port:-22}" "${host:?}" "$*"
}

fwbox_runner_picocom() { local $1; shift
    fwbox_run $PICOCOM --quiet --escape "@" --exit-after 200 --baud 115200 --initstring "$*" "${port:?}"
}

fwbox_runner_console() { local $1; shift
    fwbox_run $PICOCOM --escape "@" --baud "${baud:?}" --initstring "$*" "${port:?}"
}

fwbox_runner_zephyr_shell() {
    fwbox_run "$(printf '\r'; printf '%s\r' "$@")"
}

fwbox_runner_micropython() {
    fwbox_run "$(printf '\001'; printf '%s\004' "$@"; printf '\002')"
}

# flash: read a file from standard input and load it into the board
# $1: offset within the flash at which load the firmware
# $2: port through which send the flash command
# stdin: firmware file to send

fwbox_flash_gdb() { local host=${1:?}
    fwbox_run $GDB -q -nx -ex "target extended-remote $port" -ex "load" -ex "continue" firmware.elf
}

fwbox_flash_ecpprog() { local offset=${1:-0x00000000}
    fwbox_run $ECPPROG -a -o "$offset" -
}

# gdb: connect to a runing GDB server
# $1: host:port or serial port at which GDB is listening
# $2: ELF file to use for symbols

fwbox_gdb() { local host=${1:?} file=${2:?}
    fwbox_run $GDB -q -nx -ex "target extended $host:3333" "$file"
}

# gpioset: toggle a GPIO pin to power-cycle a board
# $1: GPIO block to control
# $2: GPIO pin to control
# $3: new state of the GPIO pin (0 or 1)

fwbox_gpioset_gpiod() { local block=${1:?} pin=${2:?} val=${3:?}
    fwbox_run gpioset --drive=push-pull "$block" "$pin" "$val"
}

fwbox_gpioset_zephyr() { local block=${1:?} pin=${2:?} val=${3:?}
    fwbox_run "gpio conf $block $pin o" "gpio set $block $pin $val"
}

fwbox_gpioset_micropython() { local block=${1:?} pin=$2 val=${3:?}
    fwbox_run "from machine import Pin" "Pin($pin, Pin.OUT).value($val)"
}

# gpioget: list GPIO blocks available
# $1: GPIO port to control (back-end specific format)
# $2: GPIO pin to control (back-end specific format)
# $3: GPIO pin to control

fwbox_gpioget_gpiod() { local port=${1:?} pin=${2:?}
    fwbox_run gpioget "$port" "$pin"
}

fwbox_gpioget_zephyr() { local port=${1:?} pin=${2:?}
    fwbox_run "gpio conf $block $pin i" "gpio get $block $pin"
}

fwbox_gpioget_micropython() { local pin=${2:?}
    fwbox_run "from machine import Pin" "Pin($pin, Pin.IN).value()"
}
