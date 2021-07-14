import re
import subprocess
import sys
from logging import getLogger

from halo import Halo
from ssm.modules.create_logger import EasyLogger


class AutoMigrate(object):
    def __init__(self):
        self.command = ['alembic', 'revision', '--autogenerate']
        self.spinner = Halo(text='Loading Now',
                            spinner={
                                'interval': 300,
                                'frames': ['-', '+', 'o', '+', '-']
                            })
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
            if re.search("Generating (.*) done", str(log).strip()) or re.search('INFO\s(.*)\sRunning\supgrade\s(.*)\s->\s(.*),\s(.*)', log) or re.search('ERROR (.*) Target database is not up to date.',
                                                                                                                                                         log):
                return 0
            elif re.search('FAILED: Can\'t locate revision identified by (.*)', log):
                return 'revision identified error'
            elif re.search('alembic: error: too few arguments', log):
                return 'too few arguments'
            print(log)
        return status

    def generate(self):
        generate_status = self.process()
        self.spinner.stop()
        if generate_status == 0:
            self.spinner.succeed('migrateファイルの生成に成功')
            self.upgrade()
        elif generate_status == 'revision identified error':
            self.spinner.fail('データベースのバージョン管理システムとの整合性が損なわれています\n再度実行し問題が修正されない場合は作者へご連絡ください')
            sys.exit(1)
        elif generate_status == 'too few arguments':
            self.spinner.fail('引数が無効です\n再度実行し問題が修正されない場合はバグですので、作者へご連絡ください。')
            sys.exit(1)
        else:
            self.spinner.fail('migrateファイルの生成に失敗\nデータベースが使用できないためサービスを終了します')
            sys.exit(1)

    def upgrade(self):
        self.spinner.start('生成したmigrateファイルを適応中')
        upgrade_status = self.process(['alembic', 'upgrade', 'head'])
        if upgrade_status == 0:
            self.spinner.succeed('migrateファイルの適応に成功')
        else:
            self.spinner.fail('migrateファイルの適応に失敗しました')
            exit('再度実行し問題が修正されない場合は作者へご連絡ください')
        return 0
