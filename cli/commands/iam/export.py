from collections import namedtuple
from typing import Optional

from boto3.session import Session

from commands.iam_context import IAMContext
from commands.types.iam import IAMCommand
from utils.utils import *


class Export(IAMCommand):
    """
    Returns audit history for a queried PS Name
    """

    def __init__(self, iam_context: IAMContext, env_session: Session,
                 all_sessions: Optional[Dict[str, Session]]):
        super().__init__(export, iam_context)
        self._all_sessions: Optional[Dict[str, Session]] = all_sessions
        self._env_session: Session = env_session

    def _write_credentials(self, access_key: str, secret_key: str, token: str, profile_name: str = 'default') -> None:
        """
        Overwrite credentials stored in the [default] profile in both ~/.aws/config and ~/.aws/credentials file
        with the provided temporary credentials. This method also CREATES these files if they do not already exist.
        """

        credentials_contents, config_contents = [], []
        default_keys = [f"[{profile_name}]\n",
                        f"aws_access_key_id = {access_key}\n",
                        f"aws_secret_access_key = {secret_key}\n",
                        f"aws_session_token = {token}\n\n"]

        default_config = [f"[profile {profile_name}]\n",
                          "output = json\n",
                          "region = us-east-1\n"]

        try:
            with open(AWS_CREDENTIALS_FILE_PATH, "r") as aws_creds:
                credentials_contents = aws_creds.readlines()

        except FileNotFoundError:
            print(f"File missing: {AWS_CREDENTIALS_FILE_PATH} - will be created.")
        finally:
            if not credentials_contents:
                contents = default_keys
            else:
                contents = self._replace_profile(f"[{profile_name}]\n", credentials_contents, replace_with=default_keys)

            os.makedirs(os.path.dirname(AWS_CREDENTIALS_FILE_PATH), exist_ok=True)
            with open(AWS_CREDENTIALS_FILE_PATH, "w+") as creds:
                creds.writelines(contents)

            print(f"{self.c.fg_gr}Successfully updated: {AWS_CREDENTIALS_FILE_PATH}{self.c.rs}")

        try:
            with open(AWS_CONFIG_FILE_PATH, "r") as aws_config:
                config_contents = aws_config.readlines()
        except FileNotFoundError:
            print(f"File missing: {AWS_CONFIG_FILE_PATH} - will be created.")
        finally:
            if not config_contents:
                contents = default_config
            else:
                contents = self._replace_profile(f"[profile {profile_name}]\n", config_contents,
                                                 replace_with=default_config)

            os.makedirs(os.path.dirname(AWS_CONFIG_FILE_PATH), exist_ok=True)
            with open(AWS_CONFIG_FILE_PATH, "w+") as creds:
                creds.writelines(contents)

            print(f"{self.c.fg_gr}Successfully updated: {AWS_CONFIG_FILE_PATH}{self.c.rs}")

    def _replace_profile(self, profile_header: str, contents: List[str], replace_with: List[str]) -> List[str]:
        """
        Replaces a profile in the provided file contents of an ~/.aws/config or ~/.aws/credentials file
        Args:
            profile_header: e.g. [default] or [profile default] - the AWS config file header to replace
            contents: List[str] The contents of the file
            replace_with: The new profile data to substitute for the previous profile
        """
        if profile_header in contents:
            default_index = contents.index(profile_header)
            del contents[default_index]
            while "[" not in contents[default_index]:
                del contents[default_index]
                if default_index > len(contents) - 1:
                    break

        contents = replace_with + ['\n'] + contents
        return contents

    def _export(self):
        if not self._all_sessions:
            credentials: namedtuple = self._env_session.get_credentials().get_frozen_credentials()
            Utils.stc_validate(credentials is not None, f"Unable to generate credentials for environment: {self.run_env}")
            self._write_credentials(credentials.access_key, credentials.secret_key, credentials.token)
        else:
            for (env, session) in self._all_sessions.items():
                credentials: namedtuple = session.get_credentials().get_frozen_credentials()
                Utils.stc_validate(credentials is not None, f"Unable to generate credentials for environment: {env}")
                self._write_credentials(credentials.access_key, credentials.secret_key, credentials.token, f"figgy-{env}")

    def execute(self):
        self._export()

