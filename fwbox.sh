# Copyright (c) 2024 Josuah Demangeon
# SPDX-License-Identifier: MIT

# Collection of shell functions to install only on the local system
# under the path /opt/fwbox/fwbox.sh

: ${GDB:=gdb-multiarch -q -nx}
: ${SSH:=ssh -C -oControlMaster=auto -oControlPath=~/.ssh/%C.sock}
: ${PICOCOM:=picocom --quiet --escape @}
: ${ECPPROG:=ecpprog -a}

# Search a ".fwbox" configuration directory and source the configuration file from here
# $1: name of the configuration file under the ".fwbox" directory

fwbox_use() { FWBOX_USE=${1:-$FWBOX_USE} FWBOX_PATH=${FWBOX_PATH:-$PWD}
    while [ -n "$FWBOX_PATH" -a ! -d "$FWBOX_PATH/.fwbox" ]; do FWBOX_PATH=${FWBOX_PATH%/*}; done
    echo "loading '$FWBOX_PATH/.fwbox/$FWBOX_USE.sh'" >&2
    . "$FWBOX_PATH/.fwbox/$FWBOX_USE.sh"
    export FWBOX_USE="$FWBOX_USE" FWBOX_PATH="$FWBOX_PATH"
}

# Send the specified command on the runner according to the chain in $FWBOX
# $@: command and argument list to execute on the target
# $FWBOX: specification of the full chain from local machine to interpreter

fwbox_run() {
    if [ -n "${FWBOX##local *}" ]; then FWBOX="local $FWBOX"; fi
    local this=${FWBOX##* }
    echo "fwbox: $@" | cat -v >&2
    FWBOX=${FWBOX% *} vars=$(IFS=,; echo $this) fwbox_runner_${this%%,*} "$@"
}

fwbox_runner_local() { local $vars
    "$@"
}

fwbox_runner_sudo() { local $vars
    fwbox_run sudo "$@"
}

fwbox_runner_ssh() { local $vars
    for x; do set -- "$@" "'$1'"; shift; done
    fwbox_run $SSH -p "${port:-22}" "${host:?}" "$*"
}

fwbox_runner_picocom() { local $vars
    fwbox_run $PICOCOM --baud "${baud:-115200}" --initstring "$*" --exit-after 200 "${port:?}"
    echo EOF >&2
}

fwbox_runner_console() { local $vars
    fwbox_run $PICOCOM --baud "${baud:-115200}" --initstring "$*" "${port:?}"
}

fwbox_runner_repl() { local $vars
    fwbox_run "$(printf '\r'; printf '%s\r' "$@")"
}

fwbox_runner_manual() { local $vars
    printf '\x1B[1m%s\x1B[m ' "fwbox: $*"
    read
}

fwbox_runner_gdb() { local $vars
    for x; do set -- "$@" -ex "$1"; shift; done
    fwbox_run $GDB -ex "target extended-remote ${port:-:3333}" "$@" "${file:?}"
}

# Read a file from standard input and load it into the board
# $1: offset within the flash at which load the firmware
# stdin: firmware file to send

fwbox_ecpprog() { local offset=${1:-0x00000000}
    fwbox_run $ECPPROG -o "$offset" -
}

# Toggle a GPIO pin to power-cycle a board
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

# List GPIO blocks available
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

# Final actions to run on the shell, taking no argument

fwbox_do_power_cycle() {
    FWBOX="$FWBOX_GPIOSET" fwbox_gpioset $FWBOX_GPIO_POWER 0
    FWBOX="$FWBOX_GPIOSET" fwbox_gpioset $FWBOX_GPIO_POWER 1
}

fwbox_do_reset() {
    FWBOX="$FWBOX_GPIOSET" fwbox_gpioset $FWBOX_GPIO_RESET 0
    FWBOX="$FWBOX_GPIOSET" fwbox_gpioset $FWBOX_GPIO_RESET 1
}

fwbox_do_hold() {
    FWBOX="$FWBOX_GPIOSET" fwbox_gpioset $FWBOX_GPIO_RESET 0
    fwbox_do_power_cycle
}

fwbox_do_console() {
    FWBOX="$FWBOX_CONSOLE" SSH="$SSH -t" fwbox_run
}

fwbox_do_dmesg() {
    fwbox_run dmesg -tc
    fwbox_run dmesg -tw
}
