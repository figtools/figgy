import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.dev.get import DevGet
from figgy.test.cli.dev.delete import DevDelete
from figgy.test.cli.dev.put import DevPut

from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *
import uuid
import time


class DevAudit(FiggyTest):

    def run(self):
        propagation_time = 75
        put = DevPut()
        guuid = uuid.uuid4().hex
        key = f"{param_test_prefix}{guuid}"
        put.add(key, DELETE_ME_VALUE, 'desc', add_more=False)
        get = DevGet()
        get.get(key, DELETE_ME_VALUE, get_more=False)
        print(f"Sleeping {propagation_time} seconds to allow for lambda -> dynamo audit log insert.")
        time.sleep(propagation_time)
        print(f"Looking up audit log for: {key}. If this fails, the lambda could be broken. ")
        self.audit(key)
        delete = DevDelete()
        delete.delete(key)

        new_uuid = uuid.uuid4().hex
        print("Testing searching for non-existent audit log.")
        self.audit(f'/doesnt/exist/{new_uuid}', expect_results=False)

    def audit(self, name, audit_another=False, expect_results=True):
        child = pexpect.spawn(f'python figgy.py config {Utils.get_first(audit)} --env {dev} --skip-upgrade', timeout=5)
        print(f"Auditing: {name}")
        child.expect('.*Please input a PS Name.*')
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
