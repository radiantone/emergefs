# type: ignore[attr-defined]
import json
from dataclasses import field

import geojson
import geopandas as gp
from geojson import FeatureCollection

import emerge.core.objects
from emerge import fs


@emerge.dataclass
class Farm(emerge.core.objects.EmergeFile):
    _shape: FeatureCollection = field(init=False, repr=False, default=None)
    crs: str = "EPSG:4326"

    @property
    def shape(self) -> FeatureCollection:
        return geojson.loads(json.dumps(self._shape))

    @shape.setter
    def shape(self, value: FeatureCollection) -> None:
        self._shape = json.loads(geojson.dumps(value))

    @property
    def geo(self):
        gdf = gp.GeoDataFrame.from_features(self._shape["features"])
        gdf.crs = self.crs
        return gdf

    def centroid(self):
        farm_gd = self.geo
        return farm_gd.to_crs(3857).centroid


# Load a farm shape
with open("data/shape/parcel1.geojson", "r") as file:
    farm1 = Farm(id="farm1", name="farmOne", path="/farms")
    farm1.shape = geojson.loads(file.read())
    fs.store(farm1)

farm = fs.getobject("/farms/farmOne", False)
print(farm)
print("CENTROID", farm.centroid())

# Load adjacent farm parcel
with open("data/shape/parcel2.geojson", "r") as file:
    farm2 = Farm(id="farm2", name="farmTwo", path="/farms")
    farm2.shape = geojson.loads(file.read())
    fs.store(farm2)

# Join the farmOne and parcelOne shapes into one big farm shape
more_land = gp.pd.concat([farm1.geo, farm2.geo])
more_land.crs = "EPSG:4326"
print(more_land)
print("CENTROID", more_land.to_crs(3857).centroid)
