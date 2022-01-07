"""
"""
from dot.mire_types.intersections import NumLegs
from pydantic import ValidationError, BaseModel
import pytest
import numpy as np


def test_numlegs_direct():
    """
    Should validate on assignment and convert types into integers
    """
    x = NumLegs(n='5')
    assert x.n == 5
    


def test_numlegs_direct_invalid():
    """
    Should raise ValidationError when invalid inputs are supplied,
    either out of range or wrong type
    """
    with pytest.raises(ValidationError):
        x = NumLegs(n=-1)

    with pytest.raises(ValidationError):
        y = NumLegs(n='one')


def test_numlegs_as_property():
    class Foo(BaseModel):
        num_legs: NumLegs

    x = Foo(num_legs=NumLegs(n=42))
    assert x.num_legs.n == 42
