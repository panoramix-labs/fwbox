# Copyright (c) 2024 Panoramix Labs
# SPDX-License-Identifier: MIT

import re
import subprocess

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
        self.speed = None
        self.count = None

    def __str__(self):
        return type(self).str(self.name, self.platform)

    @classmethod
    def scan(cls, platform: Platform) -> list[str]:
        '''Return a list of strings corresponding to devices on this platform.'''
        logger.warning(f'"scan" not implemented for {cls}')

    @classmethod
    def str(cls, name: str, platform: Platform) -> str:
        return re.sub('[^A-Za-z0-9]', '_', f'{platform}_{cls.__name__}_{name}').lower()

    @classmethod
    def add(cls, name: str, platform: Platform):
        '''Register the runner to the list of all runners if it does not exist yet.'''
        id = cls.str(name, platform)
        if id not in cls.all:
            cls.all[id] = cls(name, platform)

    def capture(self, num: int) -> str:
        '''Capture a "trace"and return the path name so it can be downloaded.'''
        logger.warning(f'"scan" not implemented for {self}')

    def ping(self) -> bool:
        '''Return a whether the connection with the runner is alive.'''
        logger.warning(f'"ping" not implemented for {self}')

    def run(self, *args, stdout=subprocess.PIPE, interactive=False):
        '''Run the runner command on the current platform.'''
        return self.platform.run(*self.command, *args, stdout=stdout, interactive=interactive)
