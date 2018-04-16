from hh_py.game_state import Vector2


def test_add_01():
    v = Vector2(5, 5) + Vector2(3, 3)

    assert v.x == 8
    assert v.y == 8


def test_sub_01():
    v = Vector2(5, 5) - Vector2(3, 3)

    assert v.x == 2
    assert v.y == 2


def test_neg_01():
    v = -Vector2(5, 5)

    assert v.x == -5
    assert v.y == -5


def test_mul_01():
    v = Vector2(5, 5) * 3

    assert v.x == 15
    assert v.y == 15


def test_iadd_01():
    v = Vector2(5, 5)
    v += Vector2(3, 3)

    assert v.x == 8
    assert v.y == 8


def test_imul_01():
    v = Vector2(5, 5)
    v *= 3

    assert v.x == 15
    assert v.y == 15


def test_getitem_01():
    v = Vector2(5, 5)

    assert v[0] == 5
    assert v[1] == 5
