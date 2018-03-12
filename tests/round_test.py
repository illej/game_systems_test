from hh_py.main import *


def test_01():
    assert round_float_to_int(1.1) == 1
    assert round_float_to_int(1.2) == 1
    assert round_float_to_int(1.3) == 1
    assert round_float_to_int(1.4) == 1
    assert round_float_to_int(1.5) == 2
    assert round_float_to_int(1.6) == 2
    assert round_float_to_int(1.7) == 2
    assert round_float_to_int(1.8) == 2
    assert round_float_to_int(1.9) == 2


def test_02():
    assert floor_float(1.3) == 1
    assert floor_float(-1.3) == -2


if __name__ == '__main__':
    test_01()
    test_02()
