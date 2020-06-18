from figcli.config import *
from figcli.utils.utils import *


class AWSCLIUtils:
    """
    Utility methods for interacting with AWSCLI resources, such as the ~/.aws/credentials and ~/.aws/config files
    """

    @staticmethod
    def write_credentials(access_key: str, secret_key: str, token: str, region: str,
                          profile_name: str = 'default', color: Color = Color(False)) -> None:
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
                          f"region = {region}\n"]

        try:
            with open(AWS_CREDENTIALS_FILE_PATH, "r") as aws_creds:
                credentials_contents = aws_creds.readlines()

        except FileNotFoundError:
            print(f"File missing: {AWS_CREDENTIALS_FILE_PATH} - will be created.")
        finally:
            if not credentials_contents:
                contents = default_keys
            else:
                contents = AWSCLIUtils._replace_profile(f"[{profile_name}]\n", credentials_contents,
                                                        replace_with=default_keys)

            os.makedirs(os.path.dirname(AWS_CREDENTIALS_FILE_PATH), exist_ok=True)
            with open(AWS_CREDENTIALS_FILE_PATH, "w+") as creds:
                creds.writelines(contents)

            print(f"\n{color.fg_gr}Successfully updated: {AWS_CREDENTIALS_FILE_PATH}{color.rs}")

        try:
            with open(AWS_CONFIG_FILE_PATH, "r") as aws_config:
                config_contents = aws_config.readlines()
        except FileNotFoundError:
            print(f"File missing: {AWS_CONFIG_FILE_PATH} - will be created.")
        finally:
            if not config_contents:
                contents = default_config
            else:
                contents = AWSCLIUtils._replace_profile(f"[profile {profile_name}]\n", config_contents,
                                                        replace_with=default_config)

            os.makedirs(os.path.dirname(AWS_CONFIG_FILE_PATH), exist_ok=True)
            with open(AWS_CONFIG_FILE_PATH, "w+") as creds:
                creds.writelines(contents)

            print(f"{color.fg_gr}Successfully updated: {AWS_CONFIG_FILE_PATH}{color.rs}")

    @staticmethod
    def _replace_profile(profile_header: str, contents: List[str], replace_with: List[str]) -> List[str]:
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
