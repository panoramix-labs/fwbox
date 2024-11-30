# Copyright (c) 2024 Panoramix Labs
# SPDX-License-Identifier: MIT

from fwbox.platform import Platform

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
        return f'{platform}.{cls.__name__}.{name}'

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
