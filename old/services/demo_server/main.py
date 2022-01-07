from fastapi import FastAPI

from dot.mire_types.osm import OSMNode
from dot.mire_types.intersections import OSMJunction, JunctionType

app = FastAPI()

@app.get('/', response_model=OSMJunction)
def root() -> OSMJunction:
    """
    return example intersection
    """
    return OSMJunction(
        junction_type=JunctionType.ROADWAY,
        num_legs=3,
        angle=85.29999999999995,
        osm_node=OSMNode(nodeid='645963548', latitude=38.9053016, longitude=-77.0147494),
        names=['New Jersey Avenue Northwest', 'New York Avenue Northwest']
    )
