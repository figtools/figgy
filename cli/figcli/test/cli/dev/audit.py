import sys

import pexpect
from figcli.test.cli.config import *
from figcli.test.cli.dev.get import DevGet
from figcli.test.cli.dev.delete import DevDelete
from figcli.test.cli.dev.put import DevPut

from figcli.test.cli.figgy import FiggyTest
from figcli.config import *
from figcli.utils.utils import *
import uuid
import time

AUDIT_PROPAGATION_TIME = 60

class DevAudit(FiggyTest):
    def __init__(self, extra_args=""):
        super().__init__(None, extra_args=extra_args)

    def run(self):
        put = DevPut(extra_args=self.extra_args)
        guuid = uuid.uuid4().hex
        key = f"{param_test_prefix}{guuid}"
        put.add(key, DELETE_ME_VALUE, 'desc', add_more=False)
        get = DevGet(extra_args=self.extra_args)
        get.get(key, DELETE_ME_VALUE, get_more=False)
        self.step(f"Sleeping {AUDIT_PROPAGATION_TIME} to allow for lambda -> dynamo audit log insert.")
        time.sleep(AUDIT_PROPAGATION_TIME)
        self.step(f"Looking up audit log for: {key}. If this fails, the lambda could be broken. ")
        self.audit(key)
        delete = DevDelete(extra_args=self.extra_args)
        delete.delete(key)

        new_uuid = uuid.uuid4().hex
        self.step("Testing searching for non-existent audit log.")
        self.audit(f'/doesnt/exist/{new_uuid}', expect_results=False)

    def audit(self, name, audit_another=False, expect_results=True):
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(audit)} --env {DEFAULT_ENV} --skip-upgrade'
                              f' {self.extra_args}', encoding='utf-8', timeout=10)
        child.logfile = sys.stdout

        self.step(f"Auditing: {name}")
        child.expect('.*Please.*input.*')
        child.sendline(name)
        if expect_results:
            child.expect(f'.*Found.*Parameter:.*{name}.*Audit another.*')
            print("Audit log found.")
        else:
            child.expect(f'.*No results found for.*{name}.*')
            print("No audit log found.")

        if audit_another:
            child.sendline('y')
        else:
            child.sendline('n')
