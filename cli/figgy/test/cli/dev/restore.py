import pexpect
from test.cli.config import *
from test.cli.figgy import FiggyTest
from test.cli.dev.put import DevPut
from test.cli.dev.delete import DevDelete
from test.cli.dev.get import DevGet
from test.cli.dev.audit import DevAudit
from config import *
from utils.utils import *
import time
import uuid


class DevRestore(FiggyTest):

    def __init__(self):
        self._guuid = uuid.uuid4().hex
        print(f"Guuid generated: {self._guuid}")

    def run(self):
        minimum, maximum = 1, 3
        first_val = 'FIRST_VAL'
        second_val = 'SECOND_VAL'
        print("Adding new configs. To Restore")
        self._setup(minimum, maximum, value_override=first_val)
        print("Waiting for propagation...")
        time.sleep(120)
        print("Validating")
        self._audit(minimum, maximum)
        restore_breakpoint_1 = int(time.time() * 1000)
        print(f"First restore breakpoint: {restore_breakpoint_1} - would expect vals of {first_val}")

        time.sleep(15)
        self._setup(minimum, maximum, value_override=second_val)
        print("Waiting for propagation...")
        time.sleep(120)
        print("Validating")
        self._audit(minimum, maximum)
        restore_breakpoint_2 = int(time.time() * 1000)
        print(f"Second restore breakpoint: {restore_breakpoint_1} - would expect vals of {second_val}")

        time.sleep(15)

        restore_prefix = f'{param_test_prefix}{self._guuid}/'
        print(f"Attempting restore to time: {restore_breakpoint_1} with prefix: {restore_prefix}")
        child = pexpect.spawn(f'python figgy.py config {Utils.get_first(restore)} --env {dev} --skip-upgrade'
                              f' --point-in-time', timeout=5)
        child.expect('.*Which.*recursively restore.*')
        child.sendline(restore_prefix)
        child.expect('.*Are you sure you want.*')
        child.sendline('y')
        child.expect('.*Seconds.*restore.*')
        child.sendline(f'{restore_breakpoint_1}')
        child.expect('.*Are you sure.*')
        child.sendline('y')
        print("Checking restore output...\r\n\r\n")
        child.expect(f'.*Value.*{param_test_prefix}{self._guuid}/test_param.*current.*Skipping.*')

        print("Validating values were rolled back...")
        time.sleep(5)

        get = DevGet()
        get.get(f'{param_test_prefix}{self._guuid}/test_param', 'NOT_CHANGED_VAL', get_more=True)
        for i in range(minimum, maximum):
            get.get(f'{param_test_prefix}{self._guuid}/test_param-{i}', first_val, get_more=i < maximum - 1)

        print("Values were rolled back successfully")
        time.sleep(30)
        print("Testing restore to second restore point")

        restore_prefix = f'{param_test_prefix}{self._guuid}/'
        print(f"Attempting restore to time: {restore_breakpoint_2} with prefix: {restore_prefix}")
        child = pexpect.spawn(f'python figgy.py config {Utils.get_first(restore)} --env {dev} --skip-upgrade'
                              f' --point-in-time', timeout=5)
        child.expect('.*Which.*recursively restore.*')
        child.sendline(restore_prefix)
        child.expect('.*Are you sure you want.*')
        child.sendline('y')
        child.expect('.*Seconds.*restore.*')
        child.sendline(f'{restore_breakpoint_2}')
        child.expect('.*Are you sure.*')
        child.sendline('y')
        print("Checking restore output...\r\n\r\n")
        child.expect(f'.*Restoring.*{param_test_prefix}{self._guuid}/test_param-2.*{second_val}.*')

        print("Validating values were rolled back...")
        time.sleep(5)

        get = DevGet()
        get.get(f'{param_test_prefix}{self._guuid}/test_param', 'NOT_CHANGED_VAL', get_more=True)
        for i in range(minimum, maximum):
            get.get(f'{param_test_prefix}{self._guuid}/test_param-{i}', second_val, get_more=i < maximum - 1)

        print("Values were rolled forward successfully. Cleaning up...")

        delete = DevDelete()
        delete.delete(f'{param_test_prefix}{self._guuid}/test_param', delete_another=True)
        for i in range(minimum, maximum):
            delete.delete(f'{param_test_prefix}{self._guuid}/test_param-{i}', delete_another=i < maximum - 1)

    def _setup(self, min: int, max: int, value_override: str = None):
        put = DevPut()
        put.add(f'{param_test_prefix}{self._guuid}/test_param', 'NOT_CHANGED_VAL', param_1_desc, add_more=True)
        for i in range(min, max):
            value = value_override if value_override else DELETE_ME_VALUE
            put.add_another(f'{param_test_prefix}{self._guuid}/test_param-{i}', value, f'{param_1_desc}-{i}',
                            add_more=i < max - 1)

        get = DevGet()
        get.get(f'{param_test_prefix}{self._guuid}/test_param', 'NOT_CHANGED_VAL', get_more=True)
        for i in range(min, max):
            value = value_override if value_override else DELETE_ME_VALUE
            get.get(f'{param_test_prefix}{self._guuid}/test_param-{i}', value, get_more=i < max - 1)

    def _audit(self, min: int, max: int):
        audit = DevAudit()
        audit.audit(f'{param_test_prefix}{self._guuid}/test_param', audit_another=True)

        for i in range(min, max):
            audit.audit(f'{param_test_prefix}{self._guuid}/test_param-{i}', audit_another=i < max - 1)
