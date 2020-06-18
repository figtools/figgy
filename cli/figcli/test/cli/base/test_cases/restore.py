import pexpect
import inspect
import re
import sys
from figcli.test.cli.base.restore import Restore


class RestoreTestSuite:

    @staticmethod
    def test_valid_role_key():
        sys.stdout.write("Testing single restore with valid role, valid key: ")

        restore = Restore(role="devops", env="dev")

        restore.choose_key(
            key="/devops/jordan/test/1", expect="Which item.+: "
        )

        restore.choose_restore_item(item_choice="2", expect=".+have it be the latest.+: ")

        restore.confirm_restore_item(".+Restore was successful\r\n")

    @staticmethod
    def test_valid_role_invalid_key():
        sys.stdout.write("Testing single restore with valid role, invalid key: ")

        restore = Restore(role="devops", env="dev")

        restore.choose_key(
            key="/devops/jordan/test/10",
            expect="No restorable values were found for this parameter.\r\n",
        )


def run():
    methods = inspect.getmembers(RestoreTestSuite, predicate=inspect.isfunction)

    for index, method in enumerate(methods):
        try:
            sys.stdout.write(f"Test #{index}: ")
            method[1]()
            sys.stdout.write("PASS\r\n")
        except pexpect.exceptions.EOF as eof:
            expected = re.findall("re.compile\(b'(.+)'\)", eof.value)[0]
            actual = re.findall("before \(last 100 chars\):.+'(.+)'", eof.value)[0]

            sys.stdout.write("FAIL\r\n")
            print(f"Expected => {expected}\r\nActual => {actual}")
        finally:
            sys.stdout.flush()


if __name__ == "__main__":
    run()