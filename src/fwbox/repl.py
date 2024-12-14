# Copyright (c) 2024 Panoramix Labs
# SPDX-License-Identifier: MIT

import cmd
import socket
import logging
import sys

from fwbox import *


RED = '\x1b[1;31m'
GREEN = '\x1b[1;32m'
YELLOW = '\x1b[1;33m'
BLUE = '\x1b[1;34m'
BOLD = '\x1b[1m'
END = '\x1b[m'

logger = logging.getLogger('fwbox')
logging.basicConfig(level=logging.INFO)


class Shell(cmd.Cmd):
    intro = '''Shell ready. Type 'help' or '?' to list commands.'''
    prompt = '>>> '
    runner = None
    log_levels = ('error', 'warning', 'info', 'debug')

    def close(self):
        pass

    def preloop(self):
        logger.info('Scanning all runners...')
        self.do_scan('')

    def do_scan(self, arg: str):
        '''Open all available runners'''
        for _, platform in Platform.all.items():
            for cls in Runner.types:
                logger.info(f'Scannning for {cls.__name__} on {platform}')
                for name in cls.scan(platform):
                    cls.add(name, platform)

    def do_ssh(self, arg: str):
        '''Add an ssh host to the list of platforms'''
        SshPlatform(arg)
        self.do_scan('')

    def do_list(self, arg: str):
        '''List all runners to check if they are still connected'''
        for name, runner in Runner.all.items():
            res = f'{GREEN}OK{END}' if runner.ping() else f'{RED}ERR{END}'
            logger.info(f'{res}:{BOLD}{name}{END}: {runner.channels}')

    def do_use(self, arg: str):
        '''Select a runner to use with other commands'''
        if arg in Runner.all:
            self.runner = Runner.all[arg]
        else:
            logger.error(f'Cannot find {arg}. Run "scan" then "list" to see all runners')
    def complete_use(self, text: str, line: str, begidx: int, endidx: int):
        return [x for x, _ in Runner.all.items() if x.startswith(text)]

    def do_capture(self, args: str):
        '''Perform a capture with the current runner and store it locally on a file'''
        if self.runner is None:
            logger.error('Select a runner first with the "use runner_name" command')
            return
        file = self.runner.capture(args.split())
        if file is not None:
            file = self.runner.platform.download(file)
            logger.info(f'Capture available at: {file}')
    def complete_capture(self, text: str, line: str, begidx: int, endidx: int):
        return [x + ' ' for x in self.runner.channels if x.startswith(text)]

    def do_pin(self, args: str):
        self.target.pin_read(args)
    def complete_pin(self, text: str, line: str, begidx: int, endidx: int):
        return [x + ' ' for x in self.runner.channels if x.startswith(text)]

    def do_pin_high(self, args: str):
        self.target.pin_write(args, True)
    def complete_pin_high(self, text: str, line: str, begidx: int, endidx: int):
        return [x + ' ' for x in self.runner.channels if x.startswith(text)]

    def do_pin_low(self, args: str):
        self.target.pin_write(args, False)
    def complete_pin_high(self, text: str, line: str, begidx: int, endidx: int):
        return [x + ' ' for x in self.runner.channels if x.startswith(text)]

    def do_pin_blink(self, args: str):
        self.target.pin_write(args, False)
    def complete_pin_high(self, text: str, line: str, begidx: int, endidx: int):
        return [x + ' ' for x in self.runner.channels if x.startswith(text)]

    def do_set_speed(self, args: str):
        '''Set the speed parameter of the runner'''
        if self.runner is None:
            logger.error('Select a runner first with the "use runner_name" command')
            return
        if len(args) == 0:
            logger.info(f'current speed is {self.runner.speed}')
        else:
            self.runner.speed = args

    def do_set_count(self, args: str):
        '''Set the number of capture samples the current runner'''
        if self.runner is None:
            logger.error('Select a runner first with the "use runner_name" command')
            return
        if len(args) == 0:
            logger.info(f'current sample count is {self.runner.count}')
        else:
            self.runner.count = args

    def do_reset(self, arg: str):
        '''Reset the list of connected runners'''
        global runners
        runners = {}

    def do_log(self, arg: str):
        '''Set log verbosity'''
        if arg.lower() in self.log_levels:
            logger.setLevel(getattr(logging, arg.upper()))
        else:
            logger.error(f'Supported log levels: {self.log_levels}')
    def complete_log(self, text: str, line: str, begidx: int, endidx: int):
        return [x + ' ' for x in self.log_levels if x.startswith(text)]

    def do_EOF(self, arg):
        '''Called when hitting Ctrl+D to quit'''
        return True


def repl():
    LocalPlatform('local')
    sh = Shell()
    sh.cmdqueue.extend(sys.argv[1:])
    sh.cmdloop()
