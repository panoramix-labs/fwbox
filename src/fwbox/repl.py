# Copyright (c) 2024 Panoramix Labs
# SPDX-License-Identifier: MIT

import cmd
import socket

from fwbox import *


RED = '\x1b[1;31m'
GREEN = '\x1b[1;32m'
YELLOW = '\x1b[1;33m'
BLUE = '\x1b[1;34m'
BOLD = '\x1b[1m'
END = '\x1b[m'


class Shell(cmd.Cmd):
    intro = '''-- Shell ready. Type 'help' or '?' to list commands.'''
    prompt = f'{BLUE}fwbox${END} '

    def parse(self, arg: str):
        return tuple(arg.split())

    def close(self):
        pass

    def preloop(self):
        print('''-- Scanning all runners...''')
        self.do_scan('')

    def do_scan(self, arg: str):
        '''Open all available runners'''

        for _, platform in Platform.all.items():
            print(f'-- platform {platform}')

            for cls in Runner.types:
                print(f'-- scannning for {cls.__name__} on {platform}')

                for name in cls.scan(platform):
                    cls.add(name, platform)

    def do_ssh(self, arg: str):
        '''Add an ssh host to the list of platforms'''
        SshPlatform(arg)
        self.do_refresh('')

    def do_reset(self, arg: str):
        '''Reset the list of connected runners'''

        global runners
        runners = {}

    def do_list(self, arg: str):
        '''List all runners to check if they are still connected'''

        for name, runner in Runner.all.items():
            res = f'{GREEN}OK{END}' if runner.ping() else f'{RED}ERR{END}'
            print(f'[{res}] {BOLD}{name}{END}: {runner.channels}')

    def do_EOF(self, arg):
        '''Called when hitting Ctrl+D to quit'''
        print('-- quitting fwbox shell')
        return self.do_quit(arg)


def repl():
    LocalPlatform(socket.gethostname())
    Shell().cmdloop()
