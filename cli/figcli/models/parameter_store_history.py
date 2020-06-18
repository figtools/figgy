from figcli.models.parameter_history import ParameterHistory
from figcli.models.restore_config import RestoreConfig
from typing import List, Set, Dict


class PSHistory:
    """
    Represents the full history of ParameterStore at a point in time.
    """

    def __init__(self, configs: List[ParameterHistory]):
        self.history: Dict[str, ParameterHistory] = {}
        for cfg in configs:
            self.history[cfg.name] = cfg

    def __str__(self):
        return f"{self.__dict__}"
