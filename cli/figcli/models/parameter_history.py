from figcli.models.restore_config import RestoreConfig
from typing import List
import json
import datetime
from decimal import *
from figcli.config import *

class ParameterHistory:
    """
    Represents the history of a single configuration with a single name.
    """

    def __init__(self):
        self.history: List[RestoreConfig] = []
        self.name = None

    @staticmethod
    def instance(cfg: RestoreConfig):
        history = ParameterHistory()
        history.add(cfg)
        return history

    def cfgs_before(self, ps_time: datetime.datetime):
        time = Decimal(ps_time.timestamp() * 1000)
        cfgs: List[RestoreConfig] = []
        for cfg in self.history:
            if cfg.ps_time < time and cfg.ps_action == SSM_PUT:
                cfgs.append(cfg)

        return sorted(cfgs, key=lambda x: x.ps_time)

    def cfg_at(self, ps_time: datetime.datetime):
        time = Decimal(ps_time.timestamp() * 1000)
        previous_cfg: RestoreConfig = None
        restore_cfg = None
        for cfg in self.history:
            if previous_cfg and previous_cfg.ps_time < time < cfg.ps_time:
                restore_cfg = previous_cfg
                break
            else:
                previous_cfg = cfg

        if not restore_cfg:
            restore_cfg = previous_cfg

        return restore_cfg

    def __eq__(self, other):
        return hash(self.__dict__) == hash(other.__dict__)

    def __hash__(self):
        return hash(self.__dict__)

    def __str__(self):
        return f"{self.__dict__}"

    def add(self, config: RestoreConfig):
        if not self.name:
            self.name = config.ps_name

        # Add and resort
        self.history.append(config)
        self.history = sorted(self.history, key=lambda x: x.ps_time)
