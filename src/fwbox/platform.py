# Copyright (c) 2024 Panoramix Labs
# SPDX-License-Identifier: MIT

import subprocess
import logging


logger = logging.getLogger('fwbox')


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

    def download(self, file):
        return file

    def run(self, *args):
        logger.debug('$ ' + ' '.join(args))
        return subprocess.run(args, stdout=subprocess.PIPE)


class SshPlatform(Platform):
    '''Local command execution'''

    opts = ('-oControlMaster=auto', '-oControlPath=%d/.ssh/%C')

    def download(self, file):
        args = ['scp', *self.opts, f'{self.name}:{file}', file]
        logger.debug('$ ' + ' '.join(args))
        if subprocess.run(args, stdout=subprocess.PIPE).returncode == 0:
            return file

    def run(self, *args):
        args = ['ssh', *self.opts, self.name] + ["'" + x.replace("'", '') + "'" for x in args]
        logger.debug('$ ' + ' '.join(args))
        return subprocess.run(args, stdout=subprocess.PIPE)
