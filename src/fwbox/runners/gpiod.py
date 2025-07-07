# Copyright (c) 2024 Panoramix Labs
# SPDX-License-Identifier: MIT

import sys
import os
import logging
import re
import subprocess

from fwbox.platform import Platform
from fwbox.runners.runner import Runner


logger = logging.getLogger('fwbox')


class GpiodRunner(Runner):
    '''
    Runner for the gpiod command to control GPIO.
    '''

    command = tuple()

    def __init__(self, name: str, platform: Platform):
        super(GpiodRunner, self).__init__(name, platform)
        stdout = self.run('gpioinfo', self.name).stdout
        for line in stdout.decode('utf8').split('\n'):
            match = re.search('line *([0-9]+): *"([^"]+)"', line)
            if match is not None and match.group(1) and match.group(2):
                logger.debug(f'Found GPIO pin {match.group(1)}_{match.group(2)}')
                self.channels.append(f'{int(match.group(1)):02}_{match.group(2)}')

    @classmethod
    def scan(cls, platform: Platform) -> list[str]:
        try:
            stdout = platform.run('gpiodetect').stdout
        except FileNotFoundError:
            logger.warning('gpiodetect command not found')
            return
        for line in stdout.decode('utf8').split('\n'):
            match = re.search('\\[([^]]+)\\]', line)
            if match and match.group(1):
                logger.debug(f'Found GPIO chip {match.group(1)}')
                yield match.group(1)

    def ping(self) -> bool:
        return self.run('gpioget', self.name, '0').returncode == 0

    def capture(self, channels: list[str]) -> bool:
        channels = [str(int(x.split('_')[0])) for x in channels]
        x = self.run('gpiomon', self.name, *channels, stdout=None, interactive=True)
        

Runner.types.append(GpiodRunner)
