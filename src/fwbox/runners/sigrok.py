# Copyright (c) 2024 Panoramix Labs
# SPDX-License-Identifier: MIT

import sys
import os
import logging

from fwbox.platform import Platform
from fwbox.runners.runner import Runner


logger = logging.getLogger('fwbox')


class SigrokRunner(Runner):
    '''
    Runner for Sigrok command line back-end: sigrok-cli.
    https://sigrok.org/
    '''

    command = ('sigrok-cli',)

    def __init__(self, name: str, platform: Platform):
        super(SigrokRunner, self).__init__(name, platform)
        self.command = self.command + ('--driver', name)
        self.speed = '8M'
        self.count = '10000'
        stdout = self.run('--show').stdout
        for line in stdout.decode('utf8').split('\n'):
            words = line.split(' ')
            if words[0:6] == ['', '', '', '', 'Logic:', 'channels']:
                self.channels.extend(words[6:])

    @classmethod
    def scan(cls, platform: Platform) -> list[str]:
        '''list all sigrok devices attached to this platform'''
        try:
            stdout = platform.run(*cls.command, '--scan').stdout
        except FileNotFoundError:
            logger.warning(f'{cls.command[0]} command not found')
            return
        for line in stdout.decode('utf8').split('\n'):
            fields = line.split(' - ')
            if len(fields) > 1:
                yield fields[0]

    def ping(self) -> bool:
        return self.run('--show').returncode == 0

    def capture(self, channels: list[str]) -> bool:
        path = f'/dev/shm/fwbox.{self}.sr'
        if os.path.isfile(path):
            os.unlink(path)
        x = self.run('--output-file', path, '--output-format', 'srzip',
                     '--samples', self.count, '--config', f'samplerate={self.speed}',
                     '--channels', ','.join(channels))
        if x.returncode == 0:
            return path
        else:
            logger.error('capture failed')

Runner.types.append(SigrokRunner)
