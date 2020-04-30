from typing import List


class CollectionUtils:
    @staticmethod
    def printable_set(frozen_set: frozenset):
        return f"{frozen_set}".replace("frozenset(", "").replace(")", "").replace("{", "").replace("}", "").replace("'",
                                                                                                                    "")

    @staticmethod
    def chunk_list(lst: List, chunk_size: int) -> List[List]:
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]