from hh_py.main import *
from hh_py.game_state import *


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


def v2_add(v1, v2):
    return v1 + v2


def test_v2_01():
    assert v2_add(Vector2(1, 1), Vector2(2, 2)) == Vector2(3, 3)


def vector2_test_02():
    v1 = Vector2(1, 1)
    v2 = Vector2(2, 2)

    result = v1 - v2

    assert result.x == -1
    assert result.y == 3


if __name__ == '__main__':
    test_01()
    test_02()
    vector2_test_01()
    vector2_test_02()
