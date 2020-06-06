import os
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
from figgy.utils.utils import Utils

CACHE_DIR = f'{HOME}/.figgy/cache'
VAULT_DIR = f'{HOME}/.figgy/vault'
c = Utils.default_colors()

# FYI I know all these tests are UGLY, but I'm ok with it, it's just tests! :)

## JORDAN: If you get EOF exceptions like this:
## pexpect.exceptions.EOF: End Of File (EOF). Empty string style platform.
## It means you created a TestObj and are calling `.expect()` on it after the child
## process has already exited. For instance, creating a single DevGet() and calling .get() numerous times.

def print_test(test: str):
    print(f"{c.fg_bl}-----------------------------------------{c.rs}")
    print(f"{c.fg_yl} Starting test: {test}{c.rs}")
    print(f"{c.fg_bl}-----------------------------------------{c.rs}")


def main():
    delete_cache(f'{CACHE_DIR}/other')
    delete_cache(f'{CACHE_DIR}/okta')
    delete_cache(f'{VAULT_DIR}/sso')
    delete_cache(f'{VAULT_DIR}/sts')

    # Test under DEV Role
    print_test("Dev Login")
    DevLogin().run()
    # print_test("Dev Put")
    # DevPut().run()
    # print_test("Dev Get")
    # DevGet().run()
    # print_test("Dev Delete")
    # DevDelete().run()
    # print_test("Dev Dump")
    # DevDump().run()
    print_test("Dev List")
    DevList().run()
    # print_test("Dev Audit")
    # DevAudit().run()
    # print_test("Dev Sync")
    # DevSync().run()
    # print_test("Dev Cleanup")
    # DevCleanup().run()
    # print_test("Dev Browse")
    # DevBrowse().run()
    # print_test("Dev Restore")
    # DevRestore().run()
    # print_test("Dev Export")
    # DevExport().run()
    # print_test("Dev Edit")
    # DevEdit().run()
    #
    # # Then Test DATA Role
    # print_test("Data Login")
    # DataLogin().run()
    # print_test("Data Put")
    # DataPut().run()
    # print_test("Data Share")
    # DataShare().run()
    # print_test("Data Sync")
    # DataSync().run()


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
