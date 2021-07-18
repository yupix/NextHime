import re
import subprocess
from logging import getLogger

from src.modules.create_logger import EasyLogger


class TooFewArguments(Exception):
    """Too Few Arguments Error notification."""
    pass


class RevisionIdentifiedError(Exception):
    """Database Revision Identified Error notification."""
    pass


class MigrateFilesGenerateError(Exception):
    """Migrate File Generate Error notification."""
    pass


class AdaptingMigrateFilesError(Exception):
    """Adapting Migrate Files Error notification."""
    pass


class AutoMigrate(object):
    def __init__(self):
        self.command = ['alembic', 'revision', '--autogenerate']
        self.logger = EasyLogger(getLogger('auto_migrate'), logger_level='DEBUG').create()

    def process(self, commands: list = None):
        if commands is None:
            command = self.command
        else:
            command = commands
        status = None
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logs = result.stdout.decode('utf-8').split('\n')
        for log in logs:
            if re.search("Generating (.*) done", str(log).strip()) or re.search('INFO\s(.*)\sRunning\supgrade\s(.*)\s->\s(.*),\s(.*)', log) or re.search(
                    'ERROR (.*) Target database is not up to date.',
                    log):
                return 0
            elif re.search('FAILED: Can\'t locate revision identified by (.*)', log):
                return 'revision identified error'
            elif re.search('alembic: error: too few arguments', log):
                return 'too few arguments'
        return status

    def generate(self):
        generate_status = self.process()
        if generate_status == 0:
            self.upgrade()
        elif generate_status == 'revision identified error':
            raise RevisionIdentifiedError
        elif generate_status == 'too few arguments':
            raise TooFewArguments
        else:
            raise MigrateFilesGenerateError

    def upgrade(self):
        upgrade_status = self.process(['alembic', 'upgrade', 'head'])
        if upgrade_status != 0:
            raise AdaptingMigrateFilesError
        return 0
