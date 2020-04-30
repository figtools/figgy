import pexpect
from test.cli.config import *
from test.cli.dev.get import DevGet
from test.cli.dev.delete import DevDelete
from test.cli.dev.put import DevPut

from test.cli.figgy import FiggyTest
from config import *
from utils.utils import *
import uuid
import time


class DevMigrate(FiggyTest):

    def run(self):
        print("YOU MUST BE ON THE SAJ VPN FOR THIS TEST TO WORK, THIS WILL NOT WORK IN CIRCLECI!!!")

        # There is some sort of weird race condition. Sometimes the test will pass, and the next run, it will fail.
        # Very confusing, but only seems to happen when running automated tests. Cannot reproduce locally.

        # /shared/automated_test/test2 has a secret, so I don't want to validate / store it here in plain text.

        print("Testing migrate automated_test to /shared/automated_test")
        self.manual_migrate('automated_test', '/shared/automated_test', {
            '/shared/automated_test/dir1/test3': DELETE_ME_VALUE,
            '/shared/automated_test/dir1/test4': DELETE_ME_VALUE,
            '/shared/automated_test/test1': DELETE_ME_VALUE,
            '/shared/automated_test/test2': '',
            '/shared/automated_test/test5': DELETE_ME_VALUE
        }, encrypted_keys=['/shared/automated_test/test2'])

        print("Testing migrate automated_test to /shared/automated_test/")
        self.manual_migrate('automated_test/', '/shared/automated_test/', {
            '/shared/automated_test/dir1/test3': DELETE_ME_VALUE,
            '/shared/automated_test/dir1/test4': DELETE_ME_VALUE,
            '/shared/automated_test/test1': DELETE_ME_VALUE,
            '/shared/automated_test/test2': '',
            '/shared/automated_test/test5': DELETE_ME_VALUE
        }, encrypted_keys=['/shared/automated_test/test2'])

        print("Testing migrate automated_test/ to /shared/automated_test")
        self.manual_migrate('automated_test/', '/shared/automated_test', {
            '/shared/automated_test/dir1/test3': DELETE_ME_VALUE,
            '/shared/automated_test/dir1/test4': DELETE_ME_VALUE,
            '/shared/automated_test/test1': DELETE_ME_VALUE,
            '/shared/automated_test/test2': '',
            '/shared/automated_test/test5': DELETE_ME_VALUE
        }, encrypted_keys=['/shared/automated_test/test2'])

        print("Testing migrate automated_test/ to /shared/automated_test/")
        self.manual_migrate('automated_test/', '/shared/automated_test/', {
            '/shared/automated_test/dir1/test3': DELETE_ME_VALUE,
            '/shared/automated_test/dir1/test4': DELETE_ME_VALUE,
            '/shared/automated_test/test1': DELETE_ME_VALUE,
            '/shared/automated_test/test2': '',
            '/shared/automated_test/test5': DELETE_ME_VALUE
        }, encrypted_keys=['/shared/automated_test/test2'])

        # # Still trying to figure out for the life of me why this doesnt' work when run by pexpect, but works
        # # when I manually test every time...
        # print("Testing migrate of individual value.")
        # self.manual_migrate('automated_test/dir1/test4', '/shared/automated_test/', {
        #         '/shared/automated_test/test4': DELETE_ME_VALUE
        # }, encrypted_keys=[])


    def manual_migrate(self, consul_prefix, dest_prefix, expected_kvs: Dict, encrypted_keys: List):
        child = pexpect.spawn(
            f'python figgy.py config {Utils.get_first(migrate)} --env {dev} --skip-upgrade --manual', timeout=10)
        # These are important, without them, PROBLEMS. LOTS OF VERY FRUSTRATING RACE CONDITION PROBLEMS
        child.delaybeforesend = 1
        child.delayafterread = 1

        child.expect(".*import from the SAJ or PM.*")
        child.sendline("saj")
        child.expect('.*consul prefix to query by.*')
        child.sendline(consul_prefix)
        child.expect('.*input a destination prefix.*')
        child.sendline(dest_prefix)
        child.expect('.*These keys and their values will be migrated.*continue.*')
        child.sendline('y')

        for key in expected_kvs.keys():
            print(f"Migrating: {key}")
            child.expect(f'.*Dest.*{key}.*Migrate.*Y/n.*')
            print("Dest matched.")
            child.sendline('y')
            print("Send sent....")
            if key in encrypted_keys:
                child.expect('.*Legacy encrypted value detected.*')
                print("Decryption success validated.")

        time.sleep(5)
        print("Performing Get(s)")
        get = DevGet()
        for key in expected_kvs.keys():
            print(f"Getting migrated Key: {key}")
            get.get(key, expected_kvs[key], get_more=key != list(expected_kvs.keys())[-1], expect_missing=False)

        print("Performing Delete(s)")
        delete = DevDelete()
        for key in expected_kvs.keys():
            print(f"Deleting: {key}")
            delete.delete(key, delete_another=key != list(expected_kvs.keys())[-1])
