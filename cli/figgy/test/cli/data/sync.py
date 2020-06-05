import sys

import pexpect

from figgy.test.cli.config import *
from figgy.test.cli.data.delete import DataDelete, DevGet
from figgy.test.cli.figgy import FiggyTest
from figgy.utils.utils import *


class DataSync(FiggyTest):

    def __init__(self):
        super().__init__(None)

    def run(self):
        self.step("Prepping workspace, deleting any existing values.")
        self.prep()

        child = pexpect.spawn(f'{CLI_NAME} {Utils.get_first(config)} {Utils.get_first(sync)} '
                              f'--env {DEFAULT_ENV} --config figgy/test/assets/data_repl_conf.json '
                              f'--skip-upgrade --replication-only', timeout=10, encoding='utf-8')
        time.sleep(2)
        with open('figgy/test/assets/data_repl_conf.json', 'r') as file:
            content = json.loads(file.read()).get('replication_config')

        self.step("Running replication-only sync and adding values.")
        sources = list(content.keys())
        for source in sources:
            child.expect(f".*input a value.*")
            child.sendline(DELETE_ME_VALUE)
            child.expect(".*description.*")
            child.sendline("desc")
            child.expect(".*secret.*")
            child.sendline('y')
            child.expect('.*encryption.*')
            child.sendline('data')
            child.expect('.*added successfully.*')

        self.step("Waiting for replication propagation")
        time.sleep(15)

        self.step("Verifying successful replication")
        destinations = list(content.values())
        for dest in destinations:
            DevGet().get(dest, DELETE_ME_VALUE, get_more=False, no_decrypt=True)

        self.step("Cleaning leftover values")
        self.prep()

    def prep(self):
        with open('figgy/test/assets/data_repl_conf.json', 'r') as file:
            content = json.loads(file.read()).get('replication_config')

        delete = DataDelete()
        destinations = list(content.values())
        for i in range(0, len(destinations)):
            print(f"DELETING: {destinations[i]}")

            if i < len(destinations):
                delete.delete(destinations[i], delete_another=True, repl_dest_delete=True)
            else:
                delete.delete(destinations[i], delete_another=False, repl_dest_delete=True)

        sources = list(content.keys())
        print(f"SOURCES: {sources}")
        for i in range(0, len(sources)):
            print(f"DELETING: {destinations[i]}")
            if i < len(sources):
                delete.delete(sources[i], delete_another=True)
            else:
                delete.delete(sources[i], delete_another=False)
