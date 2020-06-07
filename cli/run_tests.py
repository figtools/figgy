import os
import sys
from figgy.config import *
from figgy.test.cli.config import *
from figgy.test.cli.data.configure import DataConfigure
from figgy.test.cli.data.login import DataLogin
from figgy.test.cli.data.put import DataPut
from figgy.test.cli.data.share import DataShare
from figgy.test.cli.data.sync import DataSync
from figgy.test.cli.dev.audit import DevAudit
from figgy.test.cli.dev.browse import DevBrowse
from figgy.test.cli.dev.cleanup import DevCleanup
from figgy.test.cli.dev.delete import DevDelete
from figgy.test.cli.dev.dump import DevDump
from figgy.test.cli.dev.edit import DevEdit
from figgy.test.cli.dev.export import DevExport
from figgy.test.cli.dev.get import DevGet
from figgy.test.cli.dev.list import DevList
from figgy.test.cli.dev.put import DevPut
from figgy.test.cli.dev.restore import DevRestore
from figgy.test.cli.dev.sync import DevSync
from figgy.test.cli.dev.login import DevLogin
from figgy.test.cli.sso.google.configure import ConfigureGoogle
from figgy.utils.utils import Utils

CACHE_DIR = f'{HOME}/.figgy/cache'
VAULT_DIR = f'{HOME}/.figgy/vault'
CONFIG_FILE = f'{HOME}/.figgy/config'
c = Utils.default_colors()
AUTH_TYPES = ['google', 'okta', 'bastion']


# FYI I know all these tests are UGLY, but I'm ok with it, it's just tests! :)

## JORDAN: If you get EOF exceptions like this:
## pexpect.exceptions.EOF: End Of File (EOF). Empty string style platform.
## It means you created a TestObj and are calling `.expect()` on it after the child
## process has already exited. For instance, creating a single DevGet() and calling .get() numerous times.
##
## ALSO: You must always have an `child.expect` looking for the _last_ line of output, otherwise pexpect will kill
## the child process even if the child process is still finishing some stuff in the background.
def print_test(test: str):
    print(f"{c.fg_bl}-----------------------------------------{c.rs}")
    print(f"{c.fg_yl} Starting test: {test}{c.rs}")
    print(f"{c.fg_bl}-----------------------------------------{c.rs}")

def clear_cache():
    delete_cache(f'{CACHE_DIR}/other')
    delete_cache(f'{CACHE_DIR}/okta')
    delete_cache(f'{VAULT_DIR}/sso')
    delete_cache(f'{VAULT_DIR}/sts')
    delete_file(CONFIG_FILE)

def main():
    clear_cache()

    auth_type = sys.argv[1] if len(sys.argv) > 1 else "none"
    if auth_type.lower() not in AUTH_TYPES:
        raise ValueError(f'Invalid role passed in. expected params are: {AUTH_TYPES}')

    if auth_type == 'google':
        # Login to DEV Role
        print_test("Google DEV Login")
        ConfigureGoogle('dev').run()
        dev_tests()

        clear_cache()

        # Login to data role
        print_test("Data Login")
        ConfigureGoogle('data').run()
        data_tests()
    elif auth_type == 'bastion':
        # Login to DEV Role
        print_test("Bastion DEV Login")
        DevLogin().run()
        dev_tests()

        clear_cache()
        # Login to data role
        print_test("Data Login")
        DataLogin().run()
        data_tests()

    elif auth_type.lower() == 'okta':
        print_test("OKTA TESTS NOT YET IMPLEMENTED")


def dev_tests():
    print_test("Dev Put")
    DevPut().run()
    print_test("Dev Get")
    DevGet().run()
    print_test("Dev Delete")
    DevDelete().run()
    print_test("Dev Dump")
    DevDump().run()
    print_test("Dev List")
    DevList().run()
    print_test("Dev Audit")
    DevAudit().run()
    print_test("Dev Sync")
    DevSync().run()
    print_test("Dev Cleanup")
    DevCleanup().run()
    print_test("Dev Browse")
    DevBrowse().run()
    print_test("Dev Restore")
    DevRestore().run()
    print_test("Dev Export")
    DevExport().run()
    print_test("Dev Edit")
    DevEdit().run()


def data_tests():
    # Then Test DATA Role
    print_test("Data Put")
    DataPut().run()
    print_test("Data Share")
    DataShare().run()
    print_test("Data Sync")
    DataSync().run()


def devops_tests():
    pass


def delete_file(path: str):
    try:
        print(f"Deleting {path}")
        os.remove(path)
    except OSError:
        pass


def delete_cache(dir: str):
    folder = dir
    if os.path.exists(dir):
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    print(f"Deleting: {file_path}")
                    os.unlink(file_path)
            except Exception as e:
                print(e)

        try:
            if os.path.isfile(OKTA_SESSION_CACHE_PATH):
                print(f"Deleting: {OKTA_SESSION_CACHE_PATH}")
                os.unlink(OKTA_SESSION_CACHE_PATH)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
