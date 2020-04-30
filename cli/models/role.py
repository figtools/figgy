from config.aws import user_types


class Role:

    def __init__(self, role: str):
        assert role in user_types, f"Provided role must be one of: {user_types}"
        self.role = role

    def __str__(self):
        return self.role

    def __eq__(self, other):
        return self.role == other.role
