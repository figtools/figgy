from boto3.resources.base import ServiceResource

from figcli.commands.config.list import List as FigList
from figcli.commands.config.audit import Audit
from figcli.commands.config.browse import Browse
from figcli.commands.config.cleanup import Cleanup
from figcli.commands.config.delete import Delete
from figcli.commands.config.dump import Dump
from figcli.commands.config.edit import Edit
from figcli.commands.config.generate import Generate
from figcli.commands.config.promote import Promote
from figcli.commands.config.restore import Restore
from figcli.commands.config.share import *
from figcli.commands.config.sync import *
from figcli.commands.config.validate import Validate
from figcli.commands.config_context import ConfigContext
from figcli.commands.factory import Factory
from figcli.svcs.kms import KmsSvc
from figcli.svcs.auth.session_manager import SessionManager
from figcli.views.rbac_limited_config import RBACLimitedConfigView
from figcli.utils.utils import *


class ConfigFactory(Factory):
    """
    This factory is used to initialize and return all different types of CONFIG commands. For other resources, there
    would hypothetically be other factories.
    """

    def __init__(self, command: frozenset, context: ConfigContext, ssm: SsmDao, cfg: ConfigDao, kms: KmsSvc,
                 s3_resource: ServiceResource, colors_enabled: bool, config_view: RBACLimitedConfigView,
                 session_manager: SessionManager):

        self._command: frozenset = command
        self._config_context: ConfigContext = context
        self._ssm: SsmDao = ssm
        self._config: ConfigDao = cfg
        self._kms: KmsSvc = kms
        self._colors_enabled: bool = colors_enabled
        self._config_view = config_view
        self._s3_resource: ServiceResource = s3_resource
        self._utils = Utils(colors_enabled)
        self._args = context.args
        self._config_completer = self._config_view.get_config_completer()
        self._session_manager = session_manager

    def instance(self):
        return self.get(self._command)

    def get(self, command: frozenset):
        if command == sync:
            return Sync(self._ssm, self._config, self._colors_enabled, self._config_context, self.get(get),
                        self.get(put))
        elif command == cleanup:
            return Cleanup(self._ssm, self._config, self._config_context, self._config_completer,
                           self._colors_enabled, self.get(delete), args=self._args)
        elif command == put:
            return Put(self._ssm, self._colors_enabled, self._config_context, self._config_view, self.get(get))
        elif command == delete:
            return Delete(self._ssm, self._config, self._config_context, self._colors_enabled,
                          self._config_completer)
        elif command == get:
            return Get(self._ssm, self._config_completer, self._colors_enabled, self._config_context)
        elif command == share:
            return Share(self._ssm, self._config, self._config_completer, self._colors_enabled, self._config_context)
        elif command == list_com:
            return FigList(self._config_view, self._config_completer, self._colors_enabled,
                           self._config_context, self.get(get))
        elif command == browse:
            return Browse(self._ssm, self._colors_enabled, self._config_context, self.get(get),
                          self.get(delete), self._config_view)
        elif command == audit:
            return Audit(self._ssm, self._config, self._config_completer, self._colors_enabled, self._config_context)
        elif command == dump:
            return Dump(self._ssm, self._config_completer, self._colors_enabled, self._config_context)
        elif command == restore:
            return Restore(self._ssm, self._kms, self._config, self._colors_enabled, self._config_context,
                           self._config_completer, self.get(delete))
        elif command == promote:
            return Promote(self._ssm, self._config_completer, self._colors_enabled,
                           self._config_context, self._session_manager)
        elif command == edit:
            return Edit(self._ssm, self._colors_enabled, self._config_context, self._config_view, self._config_completer)
        elif command == generate:
            return Generate(self._colors_enabled, self._config_context)
        elif command == validate:
            return Validate(self._ssm, self._colors_enabled, self._config_context)
        else:
            self._utils.error_exit(f"{Utils.get_first(command)} is not a valid command. You must select from: "
                                   f"[{CollectionUtils.printable_set(config_commands)}]. Try using --help for more info.")
