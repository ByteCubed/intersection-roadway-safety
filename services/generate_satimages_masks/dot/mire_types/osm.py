"""
OpenStreetMap Object Types
--------------------------

Types to support OpenStreetMap investigations
"""
from pydantic import BaseModel, confloat


class GeoPoint(BaseModel):
    longitude: confloat(ge=-180.0, le=180.0)
    latitude: confloat(ge=-90.0, le=90.0)


class OSMNode(BaseModel):
    nodeid: str
    latitude: confloat(ge=-90.0, le=90.0)
    longitude: confloat(ge=-180.0, le=180.0)


if __name__ == "__main__":
    node = OSMNode(
        nodeid = str(29918140),
        latitude = 38.9651003,
        longitude = -77.0471434
    )
    print(node)
