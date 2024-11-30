# Copyright (c) 2024 Panoramix Labs
# SPDX-License-Identifier: MIT

# This software is a simple script with no dependency for ease of
# deployment, i.e. embedded Linux board with python pre-shipped

import cmd, sys, subprocess, socket


RED = '\x1b[1;31m'
GREEN = '\x1b[1;32m'
YELLOW = '\x1b[1;33m'
BLUE = '\x1b[1;34m'
END = '\x1b[m'


class Platform:
    '''Context where to run the shell commands: locally, on a remote system...'''

    all = {}

    def __init__(self, name: str):
        self.name = name
        self.all[str(self)] = self

    def __str__(self):
        return f'{self.name}'

    def run(self, *args):
        '''Run the given command on the current platform'''
        raise NotImplementedError('scan not implemented for this runner')

class LocalPlatform(Platform):
    '''Local command execution'''

    def run(self, *args):
        print('$ ' + ' '.join(args))
        return subprocess.run(args, stdout=subprocess.PIPE)


class SshPlatform(Platform):
    '''Local command execution'''

    def run(self, *args):
        args = ('ssh', '-oControlMaster=auto', self.name) + args
        print('$ ' + ' '.join(args))
        return subprocess.run(args, stdout=subprocess.PIPE)


class Runner:
    '''Handler for a subset of commands'''

    types = list()
    all = {}
    command = None

    def __init__(self, name: str, platform: Platform):
        self.name = name
        self.channels = list()
        self.platform = platform
        self.all[str(self)] = self

    def __str__(self):
        return type(self).str(self.name, self.platform)

    @classmethod
    def scan(cls, platform: Platform) -> list[str]:
        '''Return a list of strings corresponding to devices on this platform.'''
        raise NotImplementedError('scan not implemented for this runner')

    @classmethod
    def str(cls, name: str, platform: Platform) -> str:
        return f'{platform}:{cls.__name__}.{name}'

    @classmethod
    def add(cls, name: str, platform: Platform):
        '''Register the runner to the list of all runners if it does not exist yet.'''
        id = cls.str(name, platform)
        if id not in cls.all:
            cls.all[id] = cls(name, platform)

    def ping(self) -> bool:
        '''Return a whether the connection with the runner is alive.'''
        return False

    def run(self, *args):
        '''Run the runner command on the current platform.'''
        return self.platform.run(*self.command, *args)


class DemoRunner(Runner):
    '''
    Emulated runner without actual hardware attached to it
    '''

    @classmethod
    def scan(cls, platform: Platform) -> list[str]:
        return ['test',]

    def ping(self) -> bool:
        return True

Runner.types.append(DemoRunner)


class SigrokRunner(Runner):
    '''
    Runner for Sigrok command line back-end: sigrok-cli.
    https://sigrok.org/
    '''

    command = ('sigrok-cli',)

    def __init__(self, name: str, platform: Platform):
        super(SigrokRunner, self).__init__(name, platform)

        if ':' not in name:
            self.driver = name
            self.config = ''
        else:
            self.driver, self.config = name.split(':')

        self.command = self.command + ('--driver', self.driver, '--config', self.config)

        stdout = self.run('--show').stdout
        for line in stdout.decode('utf8').split('\n'):
            words = line.split(' ')
            if words[0:6] == ['', '', '', '', 'Logic:', 'channels']:
                self.channels.extend(words[6:])

    @classmethod
    def scan(cls, platform: Platform) -> list[str]:
        '''list all sigrok devices attached to this platform'''

        stdout = platform.run(*cls.command, '--scan').stdout
        for line in stdout.decode('utf8').split('\n'):
            fields = line.split(' - ')
            if len(fields) > 1:
                yield fields[0]

    def ping(self) -> bool:
        return self.run('--show').returncode == 0

Runner.types.append(SigrokRunner)


class Shell(cmd.Cmd):
    intro = '''-- Shell ready. Type 'help' or '?' to list commands.'''
    prompt = f'{BLUE}fwbox${END} '

    def parse(self, arg: str):
        return tuple(arg.split())

    def close(self):
        pass

    def preloop(self):
        print('''-- Scanning all runners...''')
        self.do_refresh('')

    def do_refresh(self, arg: str):
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

    def do_forget(self, arg: str):
        '''Reset the list of connected runners'''

        global runners
        runners = {}

    def do_list(self, arg: str):
        '''List all runners to check if they are still connected'''

        for name, runner in Runner.all.items():
            res = f'{GREEN}OK{END}' if runner.ping() else f'{RED}ERR{END}'
            print(f'[{res}] {name}: {runner.channels}')

    def do_EOF(self, arg):
        '''Called when hitting Ctrl+D to quit'''
        print('-- quitting fwbox shell')
        return self.do_quit(arg)


if __name__ == '__main__':
    LocalPlatform(socket.gethostname())
    Shell().cmdloop()
