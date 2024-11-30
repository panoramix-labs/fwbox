# Copyright (c) 2024 Panoramix Labs
# SPDX-License-Identifier: MIT

import sys
from fwbox.platform import Platform
from fwbox.runners.runner import Runner

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
