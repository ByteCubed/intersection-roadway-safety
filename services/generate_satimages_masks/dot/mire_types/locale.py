"""
Location types
--------------

"""
from pydantic import BaseModel, constr


class County(BaseModel):
    """
    Represent a US County

    MIRE v2.0 Item 2

    Definition: Census defined County Federal Information Processing Standard (FIPS) code or
    equivalent entity where the segment is located.

    Defined by census.gov annually.
    https://www.census.gov/geographies/reference-files/2019/demo/popest/2019-fips.html

    """
    name: str
    fips: constr(min_length=5, max_length=5)
    