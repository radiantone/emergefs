# type: ignore[attr-defined]
import json
from dataclasses import field

import geojson
from geojson import FeatureCollection

import emerge.core.objects
from emerge import fs
import geopandas as gp


@emerge.dataclass
class Farm(emerge.core.objects.EmergeFile):
    _shape: FeatureCollection = field(init=False, repr=False, default=None)

    @property
    def shape(self) -> FeatureCollection:
        return geojson.loads(json.dumps(self._shape))

    @shape.setter
    def shape(self, value: FeatureCollection) -> None:
        self._shape = json.loads(geojson.dumps(value))


with open("data/shape/DarrenFarm.geojson", "r") as file:
    farm = Farm(id="farm1", name="farmOne", path="/farms")
    farm.shape = geojson.loads(file.read())
    fs.store(farm)

farm = fs.getobject("/farms/farmOne", False)
print(farm)
gdf = gp.GeoDataFrame.from_features(farm.shape['features'])
gdf.crs = "EPSG:4326"
print("CENTROID", gdf.to_crs(3857).centroid)
