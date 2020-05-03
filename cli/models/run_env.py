
class RunEnv:

    def __init__(self, env):
        self.env = env

    def __str__(self):
        return self.env

    def __eq__(self, obj):
        if isinstance(obj, RunEnv):
            return obj.env == self.env

        return False
