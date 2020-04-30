from commands.factory import Factory
from config import *
from commands.config.cleanup import Cleanup
from commands.config.delete import Delete
from commands.config.get import Get
from commands.config.migrate import Migrate
from commands.config.audit import Audit
from commands.config.promote import Promote
from commands.config.put import Put
from commands.config.share import *
from commands.config.dump import Dump
from commands.config.sync import *
from commands.config.browse import Browse
from commands.config_context import ConfigContext
from commands.config.restore import Restore
from commands.config.edit import Edit
from commands.config.generate import Generate
from svcs.cache_manager import CacheManager
from prompt_toolkit.completion import WordCompleter
import commands.config.list
from utils.utils import *
from svcs.kms import KmsSvc
from svcs.config import ConfigService
from boto3.resources.base import ServiceResource


# Todo move many of these init variables into context, pass in hydrated context.
class ConfigFactory(Factory):
    """
    This class wasn't so bad when there were like 4 commands, now it's kinda insane and I apologize.
    #Todo - Do something better. Dependency injection, etc.

    This factory is used to initialize and return all different types of CONFIG commands. For other resources, there
    would hypothetically be other factories.
    """

    def __init__(self, command: frozenset, context: ConfigContext, ssm: SsmDao, cfg: ConfigDao, kms: KmsSvc,
                 s3_resource: ServiceResource, colors_enabled: bool, config_completer: WordCompleter,
                 dest_ssm: SsmDao = None):

        self._command: frozenset = command
        self._config_context: ConfigContext = context
        self._ssm: SsmDao = ssm
        self._config: ConfigDao = cfg
        self._kms: KmsSvc = kms
        self._colors_enabled: bool = colors_enabled
        self._config_completer = config_completer
        self._s3_resource: ServiceResource = s3_resource
        self._utils = Utils(colors_enabled)
        self._args = context.args
        self._dest_ssm: SsmDao = dest_ssm

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
            return Put(self._ssm, self._colors_enabled, self._config_context, self._config_completer, self.get(get))
        elif command == delete:
            return Delete(self._ssm, self._config, self._config_context, self._colors_enabled,
                          self._config_completer)
        elif command == get:
            return Get(self._ssm, self._config_completer, self._colors_enabled, self._config_context)
        elif command == share:
            return Share(self._ssm, self._config, self._config_completer, self._colors_enabled, self._config_context)
        elif command == list_com:
            return commands.config.list.List(self._ssm, self._config_completer,
                                             self._colors_enabled, self._config_context,
                                             self.get(get))
        elif command == migrate:
            return Migrate(self._ssm, self._kms, self._s3_resource, self._colors_enabled, self._config_context,
                           self._config_completer)
        elif command == browse:
            return Browse(self._ssm, self._config, self._colors_enabled, self._config_context, self.get(get),
                          self.get(delete))
        elif command == audit:
            return Audit(self._ssm, self._config, self._config_completer, self._colors_enabled, self._config_context)
        elif command == dump:
            return Dump(self._ssm, self._config_completer, self._colors_enabled, self._config_context)
        elif command == restore:
            return Restore(self._ssm, self._kms, self._config, self._colors_enabled, self._config_context,
                           self._config_completer, self.get(delete))
        elif command == promote:
            return Promote(self._ssm, self._dest_ssm, self._config_completer, self._colors_enabled,
                           self._config_context)
        elif command == edit:
            return Edit(self._ssm, self._colors_enabled, self._config_context, self._config_completer)
        elif command == generate:
            return Generate(self._colors_enabled, self._config_context)

        else:
            self._utils.error_exit(f"{Utils.get_first(command)} is not a valid command. You must select from: "
                                   f"[{Utils.printable_set(config_commands)}]. Try using --help for more info.")
