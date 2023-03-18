import json
from dataclasses import field

import geojson
from geojson import FeatureCollection

import emerge.core.objects
from emerge import fs


@emerge.dataclass
class Farm(emerge.core.objects.EmergeFile):
    shape: FeatureCollection = field(init=False, repr=False, default=None)


with open("data/shape/DarrenFarm.geojson", "r") as farm:
    shape = geojson.loads(farm.read())
    farm = Farm(id="farm1", name="farmOne", path="/farms")
    farm.shape = json.loads(geojson.dumps(shape))
    print(farm)
    fs.store(farm)
