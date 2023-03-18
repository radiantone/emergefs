# type: ignore[attr-defined]
import json
from dataclasses import field

import geojson
from geojson import FeatureCollection

import emerge.core.objects
from emerge import fs


@emerge.dataclass
class Farm(emerge.core.objects.EmergeFile):
    _shape: FeatureCollection = field(init=False, repr=False, default=None)

    @property
    def shape(self) -> FeatureCollection:
        return geojson.loads(json.dumps(self._shape))

    @shape.setter
    def shape(self, value: FeatureCollection) -> None:
        self._shape = json.loads(geojson.dumps(value))


with open("data/shape/DarrenFarm.geojson", "r") as farm:
    shape = geojson.loads(farm.read())
    farm = Farm(id="farm1", name="farmOne", path="/farms")
    farm.shape = json.loads(geojson.dumps(shape))
    fs.store(farm)

farm = fs.getobject("/farms/farmOne", False)
print(farm)
print(farm.shape)
