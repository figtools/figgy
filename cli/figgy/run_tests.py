import os

from config import *
from test.cli.config import *
from test.cli.data.configure import DataConfigure
from test.cli.dev.audit import DevAudit
from test.cli.dev.auth import DevAuth
from test.cli.dev.browse import DevBrowse
from test.cli.dev.cleanup import DevCleanup
from test.cli.dev.configure import DevConfigure
from test.cli.dev.delete import DevDelete
from test.cli.dev.dump import DevDump
from test.cli.dev.export import DevExport
from test.cli.dev.find import DevFind
from test.cli.dev.get import DevGet
from test.cli.dev.list import DevList
from test.cli.dev.put import DevPut
from test.cli.dev.restore import DevRestore
from test.cli.dev.run_tests import DevRunTests
from test.cli.dev.sync import DevSync
from test.cli.dev.zip import DevZip
from test.cli.init import CLIInit


def main():
    # This is used when running in CircleCi
    if MFA_SECRET_ENV_KEY in os.environ \
            and MFA_USER_ENV_KEY in os.environ:
        print(f"{MFA_SECRET_ENV_KEY} FOUND, configuring with MFA for data/devops/dev roles..")
        print("Deleting any existing cached credentials...")
        delete_cache()
        CLIInit.init('dev')

    # Order matters. Put must come before delete, etc.

    # Test DEV Role first.
    DevConfigure().run()
    DevPut().run()
    DevGet().run()
    DevDelete().run()
    DevDump().run()
    DevList().run()
    DevAudit().run()
    DevSync().run()
    DevCleanup().run()
    DevBrowse().run()
    DevRestore().run()
    DevExport().run()
    DevAuth().run()
    DevFind().run()
    DevZip().run()
    DevRunTests().run()
    # DevEdit().run() -- Currently busted...
    # # Then Test DATA Role
    DataConfigure().run()
    # DataShare().run()


def delete_cache():
    folder = CACHE_DIR
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
