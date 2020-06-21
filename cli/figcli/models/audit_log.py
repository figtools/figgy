import time


class AuditLog:
    """
    Represents a singular audit log retrieved from our config-auditor table.
    """
    def __init__(self, parameter_name: str, time: int, action: str, user: str):
        self.parameter_name = parameter_name
        self.time = time
        self.action = action
        self.user = user

    def __str__(self):
        return f"Parameter: {self.parameter_name}\n" \
               f"Time: {time.ctime(int(self.time / 1000))}\n" \
               f"User: {self.user}\n" \
               f"Action: {self.action}\n"
