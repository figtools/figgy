import re
from typing import Set, Dict
from figcli.config import *


class KeyUtils(object):

    @staticmethod
    def find_all_expected_names(config_keys: set, shared_names: set, merge_conf: dict,
                                repl_conf: dict, repl_from_conf: dict, namespace: str) -> Set[str]:
        """
        From various sets of keys and configs, calculates all required PS Names (keys) this application requires.
        Args:
            config_keys: set -> representing the app_figs in the passed in figgy.json file
            shared_names: set -> representing the shared_figs in the passed in figgy.json file
            merge_conf: dict -> representing the merged_figs in the passed in figgy.json file
            repl_conf: dict -> representing the replicate_figs in the figgy.json file
            repl_from_conf: dict -> represents the `replicate_from` config block in the figgy.json file
            namespace: parsed, or calculated namespace for the application being synced. E.G. /app/demo-time/

        Returns: Set[str] -> All PS Names that have been defined as dependencies for this application's deployment
        """
        merge_keys = set(merge_conf.keys())
        all_keys = config_keys | shared_names | merge_keys

        for merge_key, merge_val in merge_conf.items():
            if type(merge_val) == list:
                for val in merge_val:
                    if KeyUtils.sanitize(val).startswith(namespace):
                        all_keys.add(KeyUtils.sanitize(val))
            elif type(merge_val) == str:
                matches = re.findall('\${([\w/-]+)}', merge_val)
                for match in matches:
                    if match.startswith(namespace):
                        all_keys.add(KeyUtils.sanitize(match))

        for key in repl_conf:
            all_keys.add(repl_conf[key])

        source_ns = repl_from_conf.get(SOURCE_NS_KEY)
        params = repl_from_conf.get(PARAMETERS_KEY)

        if source_ns and params:
            for param in params:
                all_keys.add(f'{namespace}{param}')

        return all_keys


    @staticmethod
    def merge_repl_and_repl_from_blocks(repl_conf: Dict, repl_from: Dict, dest_namespace: str) -> Dict:
        """
        Parses the repl_from block and merges it into the standard 'replication' block. This simplifies
        configuring replication and detecting orphans.
        Args:
            repl_conf: Dict representing the `replicate_figs` block in figgy.json file
            repl_from: Dict representing the `replicate_frorm` block in figgy.json file
            dest_namespace: namespace found in the `figgy.json` file. Where replication is destined for.

        Returns: an updated repl_conf dictionary with repl_from figcli.configs merged into it.
        """

        source_ns = repl_from.get(SOURCE_NS_KEY)
        params = repl_from.get(PARAMETERS_KEY)
        dest_namespace = dest_namespace if dest_namespace.endswith('/') else f'{dest_namespace}/'

        if source_ns and params:
            source_ns = source_ns if source_ns.endswith('/') else f'{source_ns}/'
            for param in params:
                repl_conf[f'{source_ns}{param}'] = f'{dest_namespace}{param}'

        return repl_conf

    @staticmethod
    def sanitize(merge_val):
        return merge_val.replace("${", "").replace("}", "").replace(merge_uri_suffix, "")

    @staticmethod
    def desanitize(merge_val):
        return "${" + merge_val + "}"
