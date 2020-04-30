from config.aws import envs


class RunEnv:

    def __init__(self, env):
        assert env in envs, f"Provided run_env must be one of: {envs}"
        self.env = env

    def __str__(self):
        return self.env

    def __eq__(self, obj):
        if isinstance(obj, RunEnv):
            return obj.env == self.env

        return False
