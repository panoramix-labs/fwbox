# Copyright (c) 2024 Panoramix Labs
# SPDX-License-Identifier: MIT

import subprocess


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
