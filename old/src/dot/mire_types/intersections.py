"""
At-Grade Intersection/Junctions
-------------------------------

"""

from enum import IntEnum, IntFlag, auto
from typing import Optional, List
from pydantic import BaseModel, validator, confloat, root_validator
from .osm import OSMNode
import pygeohash
import warnings



class JunctionType(IntFlag):
    """
    Element 111: Type of Intersection/Junction

    Definition: Type of junction being described in the data record. Recommended Attributes:

        1. Roadway/roadway (not interchange related)
        2. Roadway/roadway (interchange ramp terminal)
        3. Roadway/pedestrian crossing (e.g., midblock crossing, pedestrian path or trail)
        4. Roadway/bicycle path or trail
        5. Roadway/railroad grade crossing
        6. Other
    """
    ROADWAY = auto()
    INTERCHANGE_RAMP = auto()
    PEDESTRIAN = auto()
    BICYCLE_OR_TRAIL = auto()
    RAILROAD = auto()
    OTHER = auto()


class NumLegs(int):
    """
    Element 115: Intersection/Junction Number of Legs

    The number of legs of an intersection should be a strictly positive integer.

    This is a subclass of int that enforces the positive integer constraint.
    :py:meth:`validate` allows this type to be used within Pydantic BaseModels.
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val):
        """
        Cast value to integer, if possible, and assert value is positive

        Raises
        ------
        TypeError
            input cannot be casted to int
        AssertionError
            input value is non-positive

        """
        val = int(val)   
        assert val >= 1, f"{cls.__name__} objects must be integers >= 1"
        return val

    def __new__(cls, val, **kwargs):
        return super().__new__(cls, cls.validate(val))


class IntersectionGeometryTypes(IntEnum):
    """
    Element 116: Intersection/Junction Geometry

    Definition: The type of geometric configuration that best describes the intersection/junction.    
    """
    T = 1
    """T-Intersection"""

    Y = 2
    """Y-Intersection"""

    CROSS = 3
    """Cross-Intersection (four legs)"""
    
    MULTI_NOT_CIRCULAR = 4
    """Five or more legs and not circular"""

    ROUNDABOUT = 5
    """Roundabout"""

    OTHER_CIRCULAR = 6
    """Other circular intersection (e.g., rotaries, neighborhood traffic circles)"""

    PEDESTRIAN = 7
    """Midblock pedestrian crossing"""

    RESTRICTED_U = 8
    """Restricted crossing U-turn (i.e., RCUT, J-turn, Superstreet) intersection"""

    MEDIAN_U = 9
    """Median U-turn (i.e., MUT, Michigan Left, Thru-turn) intersection"""

    DISPLACED_LEFT = 10
    """Displaced left-turn (i.e., DLT, continuous flow, CFI) intersection"""
    
    JUGHANDLE = 11
    """Jughandle (i.e., New Jersey jughandle) intersection"""

    CONTINUOUS_T = 12
    """Continuous green T intersection"""

    QUADRANT = 13
    """Quadrant (i.e., quadrant roadway) intersection"""

    OTHER = 14
    """Other"""


class IntersectionGeometry(BaseModel):
    """
    Intersection Geometry information combining elements 111, 114 and 115

    Type of intersection, number of legs, and geometry all have
    correlated constraints. This class validates information based on these
    constraints.
    """
    junction_type: JunctionType
    num_legs: NumLegs
    geometry: IntersectionGeometryTypes


    @validator('num_legs')
    def check_num_legs_matches_geometry(cls, val, values):
        """
        Ensure the number of legs information is in concordance with
        geometry.

        .. warning:: **WORK IN PROGRESS**

            Unknowns:

                * constraints on types like U-turns and jughandles
                * constraints on pedestrian crosswalks
        """
        if values['junction_type'] in {
                IntersectionGeometryTypes.T,
                IntersectionGeometryTypes.Y}:
            assert val == 3

        elif values['junction_type'] == IntersectionGeometryTypes.CROSS:
            assert val == 4

        elif values['junction_type'] == IntersectionGeometryTypes.MULTI_NOT_CIRCULAR:
            assert val >= 5

        return val

    @validator('junction_type')
    def check_junction_type_matches_geometry(cls, val, values):
        """
        Ensure junction type matches geometry

        For example, pedestrian crosswalk must be PEDESTRIAN junction type

        .. warning:: **WORK IN PROGRESS**

            Still need to implement most of the logic of the constraints between
            types.

        """
        if values['junction_type'] == IntersectionGeometryTypes.PEDESTRIAN:
            assert val == JunctionType.PEDESTRIAN

        return val


class IntersectingAngle(float):
    """
    Element 119: Intersecting Angle

    Definition: The measurement in degrees of the smallest
    angle between any two legs of the intersection.
    This value will always be within a range of 0 to 90 degrees
    (i.e., for non-zero angles, always measure the acute rather than the obtuse angle).

    This object will raise a warning if a provided angle is obtuse and will convert
    to its dual acute angle (180-x).
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val):
        """
        Cast value to an acute angle in degrees,
        represented as a float

        Raises
        ------
        TypeError
            input cannot be casted to float
        AssertionError
            input value is out of bounds for degrees
        RuntimeWarning
            input angle is obtuse and is automatically converted to acute

        """
        val = float(val)
        assert 0.0 <= val <= 360.0, f"Value ({val}) is not a valid angle"
        if val > 90.0:
            warnings.warn(
                "Intersection angle provided is obtuse. We are automatically converting to an acute angle to match MIRE spec.",
                RuntimeWarning
            )
            if val // 180:
                val -= 180.0
            val = 180.0 - val
        return val

    def __new__(cls, val, **kwargs):
        return super().__new__(cls, cls.validate(val))


class NumLanes(int):
    """
    Element XXX: (need to check if part of MIRE)

    The number of lanes of an intersection should be a strictly positive integer.

    This is a subclass of int that enforces the positive integer constraint.
    :py:meth:`validate` allows this type to be used within Pydantic BaseModels.
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val):
        """
        Cast value to integer, if possible, and assert value is positive

        Raises
        ------
        TypeError
            input cannot be casted to int
        AssertionError
            input value is non-positive

        """
        val = int(val)
        assert val >= 0, f"{cls.__name__} objects must be integers >= 0"
        return val

    def __new__(cls, val, **kwargs):
        return super().__new__(cls, cls.validate(val))


class ProportionOneway(int):
    """
    Element XXX: (need to check if part of MIRE)

    The proportion of oneway road segments of an intersection should be a positive float
    from 0 to 1.

    This is a subclass of int that enforces the positive integer constraint.
    :py:meth:`validate` allows this type to be used within Pydantic BaseModels.
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, val):
        """
        Cast value to integer, if possible, and assert value is positive

        Raises
        ------
        TypeError
            input cannot be casted to float
        AssertionError
            input value is non-positive

        """
        val = float(val)
        assert val >= 0 and val <= 1, f"{cls.__name__} objects must be floats >= 0 & <= 1"
        return val

    def __new__(cls, val, **kwargs):
        return super().__new__(cls, cls.validate(val))


class OSMJunction(BaseModel):
    """A single junction matching MIRE, along with source OSM data
    """
    junction_type: Optional[JunctionType] = None
    num_legs: Optional[NumLegs] = None
    geometry_type: Optional[IntersectionGeometryTypes] = None
    geometry: Optional[IntersectionGeometry] = None
    angle: Optional[IntersectingAngle] = None
    lanes: Optional[NumLanes] = None
    oneway: Optional[ProportionOneway] = None

    longitude: confloat(ge=-180.0, le=180.0)
    latitude: confloat(ge=-90.0, le=90.0)

    nodeid:  str = ''  # geohash

    names: Optional[List[str]] = None
    # osm_adjacent_edges

    @root_validator()
    def create_nodeid(cls, values):
        """
        Use geohash to create a nodeid from longitude and latitude
        """
        try:
            values['nodeid'] = pygeohash.encode(values['latitude'], values['longitude'])
        except KeyError as e:
            print(values)
            raise e
        return values
