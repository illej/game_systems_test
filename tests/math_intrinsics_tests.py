from hh_py.main import *


def test_round_01():
    assert round_float_to_int(1.1) == 1
    assert round_float_to_int(1.2) == 1
    assert round_float_to_int(1.3) == 1
    assert round_float_to_int(1.4) == 1
    assert round_float_to_int(1.5) == 2
    assert round_float_to_int(1.6) == 2
    assert round_float_to_int(1.7) == 2
    assert round_float_to_int(1.8) == 2
    assert round_float_to_int(1.9) == 2


def test_floor_01():
    assert floor_float(1.3) == 1
    assert floor_float(-1.3) == -2


def test_sqrt():
    assert square_root(25) == 5
    assert math.sqrt(25) == 5


def test_min_max():
    assert minimum(1, 2) == 1
    assert minimum(2, 1) == 1
    assert maximum(1, 2) == 2
    assert maximum(2, 1) == 2
