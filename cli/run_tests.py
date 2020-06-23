import os
import sys
from figcli.config import *
from figcli.test.cli.config import *
from figcli.test.cli.data.configure import DataConfigure
from figcli.test.cli.data.login import DataLogin
from figcli.test.cli.data.put import DataPut
from figcli.test.cli.data.share import DataShare
from figcli.test.cli.data.sync import DataSync
from figcli.test.cli.dev.audit import DevAudit
from figcli.test.cli.dev.validate import DevValidate
from figcli.test.cli.dev.browse import DevBrowse
from figcli.test.cli.dev.cleanup import DevCleanup
from figcli.test.cli.dev.delete import DevDelete
from figcli.test.cli.dev.dump import DevDump
from figcli.test.cli.dev.edit import DevEdit
from figcli.test.cli.dev.export import DevExport
from figcli.test.cli.dev.get import DevGet
from figcli.test.cli.dev.list import DevList
from figcli.test.cli.dev.put import DevPut
from figcli.test.cli.dev.restore import DevRestore
from figcli.test.cli.dev.sync import DevSync
from figcli.test.cli.dev.login import DevLogin
from figcli.test.cli.sso.google.configure import ConfigureGoogle
from figcli.utils.utils import Utils
from figcli.test.cli.sso.okta.configure import ConfigureOkta

CACHE_DIR = f'{HOME}/.figgy/cache'
VAULT_DIR = f'{HOME}/.figgy/vault'
CONFIG_FILE = f'{HOME}/.figgy/config'
KEYRING_FILE = f'{HOME}/.local/share/python_keyring/keyring_pass.cfg'
c = Utils.default_colors()
AUTH_TYPES = ['google', 'okta', 'bastion', 'profile']


# FYI I know tests are a bit UGLY, but I'm ok with it, it's just tests! :)

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


def run_test(test_name: str, test):
    print_test(test_name)
    klass = test.__class__.__name__
    env_override = f'{Utils.to_env_var(klass)}_DISABLED'
    if os.environ.get(env_override) == "true":
        print(f"{c.fg_bl}-----------------------------------------{c.rs}")
        print(f"{c.fg_yl} Skipping test: {klass} due to presence of {env_override} environment variable. {c.rs}")
        print(f"{c.fg_bl}-----------------------------------------{c.rs}")

    else:
        test.run()


def clear_cache():
    delete_cache(f'{CACHE_DIR}/other')
    delete_cache(f'{CACHE_DIR}/okta')
    delete_cache(f'{VAULT_DIR}/sso')
    delete_cache(f'{VAULT_DIR}/sts')
    delete_file(CONFIG_FILE)
    delete_file(KEYRING_FILE)


def main():
    clear_cache()

    auth_type = sys.argv[1] if len(sys.argv) > 1 else "none"
    profile = sys.argv[2] if len(sys.argv) > 2 else "none"
    BASTION_ENV = os.environ.get("ENV_OVERRIDE") or DEFAULT_ENV

    if auth_type.lower() not in AUTH_TYPES:
        raise ValueError(f'Invalid role passed in. expected params are: {AUTH_TYPES}')

    if auth_type == 'google':
        # Login to DEV Role
        print_test("Google DEV Login")
        ConfigureGoogle('dev').run()
        dev_tests(key_down_to_shared=1)

        clear_cache()

        # Login to data role
        print_test("Data Login")
        ConfigureGoogle('data').run()
        data_tests()
    elif auth_type == 'bastion':
        # Login to DEV Role
        print_test("Bastion DEV Login")
        DevLogin(BASTION_ENV).run()
        dev_tests(key_down_to_shared=1)

        clear_cache()
        # Login to data role
        print_test("Data Login")
        DataLogin().run()
        data_tests()

    elif auth_type.lower() == 'okta':
        print_test("OKTA DEV Login")
        ConfigureOkta('dev').run()
        dev_tests(key_down_to_shared=1)

        clear_cache()

        # Login to data role
        print_test("Data Login")
        ConfigureOkta('data').run()
        data_tests()

    elif auth_type.lower() == 'profile':
        dev_tests(profile=profile, key_down_to_shared=4)
        clear_cache()


def dev_tests(profile=None, key_down_to_shared=4):
    extra_args = f"--profile {profile}" if profile else ""

    run_test("Dev Put", DevPut(extra_args=extra_args))
    run_test("Dev Get", DevGet(extra_args=extra_args))
    run_test("Dev Delete", DevDelete(extra_args=extra_args))
    run_test("Dev Dump", DevDump(extra_args=extra_args))
    run_test("Dev List", DevList(extra_args=extra_args))
    run_test("Dev Audit", DevAudit(extra_args=extra_args))
    run_test("Dev Sync", DevSync(extra_args=extra_args))
    run_test("Dev Cleanup", DevCleanup(extra_args=extra_args))
    print(f"Key down: {key_down_to_shared}")
    run_test("Dev Browse", DevBrowse(extra_args=extra_args, key_down_to_shared=key_down_to_shared))
    run_test("Dev Restore", DevRestore(extra_args=extra_args))
    run_test("Dev Export", DevExport(extra_args=extra_args))
    run_test("Dev Edit", DevEdit(extra_args=extra_args))
    run_test("Dev Validate", DevValidate(extra_args=extra_args))


def data_tests():
    # Then Test DATA Role
    run_test("Data Put", DataPut())
    run_test("Data Share", DataShare())
    run_test("Data Sync", DataSync())


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
