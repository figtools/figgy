import click
from botocore.exceptions import ClientError
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from figcli.commands.config.get import Get
from figcli.commands.config_context import ConfigContext
from figcli.commands.types.config import ConfigCommand
from figcli.config.style.style import FIGGY_STYLE
from figcli.data.dao.ssm import SsmDao
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker
from figcli.utils.utils import *
from figcli.views.rbac_limited_config import RBACLimitedConfigView


class List(ConfigCommand):

    def __init__(self, config_view: RBACLimitedConfigView, config_completer_init: WordCompleter,
                 colors_enabled: bool, config_context: ConfigContext, get: Get):
        super().__init__(list_com, colors_enabled, config_context)
        self._view = config_view
        self._config_completer = config_completer_init
        self._get = get
        self._utils = Utils(colors_enabled)

    def _list_params(self):
        """
        Prompts user for a namespace of parameters to query. Once queried, user may select from the outputted chart
        of found parameters matching that namespace. This will then provide the user the selected value.
        """

        # Prompts for this file
        select_message = [
            (f'class:{self.c.bl}', '`[1-999]` '),
            ('class:', 'to select a value. '),
            (f'class:{self.c.bl}', '`continue` '),
            ('class:', 'to query more. Anything else quits. \n\nSelection: ')
        ]

        # Add all keys
        list_another = True

        while list_another:
            print()
            namespace = prompt(f"Please input a namespace prefix to query: ", completer=self._config_completer)
            if not self._utils.is_valid_input(namespace, "namespace", notify=False):
                continue

            print(f"Passing in prefix of :{namespace}")
            parameters = self._view.get_config_names(prefix=namespace)
            names = [['Selector', 'Name']]
            count = 1
            for param in parameters:
                names.append([f'{self.c.fg_rd}{count}{self.c.rs}', param])
                count = count + 1

            # Pretty print out with columns for selection.
            data = '\n'.join(['\t'.join([str(cell) for cell in row]) for row in names])
            keep_getting = True

            while keep_getting:
                pagination_threshold = 30
                if count > pagination_threshold:
                    pagination_data = f"Find your number, then use \"q\" to quit. Then input your number.\n\n {data}"
                    click.echo_via_pager(pagination_data)
                else:
                    pagination_data = data
                    click.echo(pagination_data)

                selection = prompt(select_message, style=FIGGY_STYLE)
                if re.match('[0-9]+', selection) is not None:
                    if int(selection) > count - 1:
                        print(f"Invalid selection. try again")
                        continue
                    print(f"Name: {names[int(selection)][1]}")
                    value, desc = self._get.get_val_and_desc(names[int(selection)][1])
                    desc = desc if desc else DESC_MISSING_TEXT

                    if value is not None:
                        print(f"Value: {value}")
                        print(f"{self.c.fg_gr}Description: {self.c.rs}{desc}")

                    hold = input(f"\nPress ENTER when you want to look up another value.")
                    click.clear()
                else:
                    list_another = selection.lower() == "continue"
                    keep_getting = False

    @VersionTracker.notify_user
    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self._list_params()
