import dataclasses
import json
from typing import Any

from persistent import Persistent


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class EmergeData(Persistent):

    data: Any

    def __str__(self):
        return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)
