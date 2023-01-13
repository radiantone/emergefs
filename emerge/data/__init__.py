import dataclasses
import datetime
import json
from dataclasses import dataclass
from typing import Any

from persistent import Persistent


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclass
class EmergeData(Persistent):

    id: str
    data: Any
    date: str = str(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S"))

    def __str__(self):
        # return json.dumps(self, indent=4, cls=EnhancedJSONEncoder)
        return json.dumps(dataclasses.asdict(self))
