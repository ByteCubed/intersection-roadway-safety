"""
GeoJSON Utilities
-----------------

"""

def make_point(lon: float, lat: float, **properties):
    """Create a geojson Point object

    Parameters
    ----------
    lon: 
        Longitude
    lat:
        Latitude
    properties:
        extra keyword arguments can get added as metadata to the Point.
    """
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        },
        "properties": dict(**properties)
    }


def make_point_collection(points: list):
    return {
        "type": "FeatureCollection",
        "features": points
    }
