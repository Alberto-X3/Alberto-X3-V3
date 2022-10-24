import copy
import pytest

from AlbertoX3 import colors


__all__ = ()


_INT: int = 1337
_DICT: dict[int | str, int] = {42: 69, "one": 1}


@pytest.fixture()
def nested_int() -> colors.NestedInt:
    return colors.NestedInt(_INT, _DICT)


def test_nested_int(nested_int: colors.NestedInt):
    assert type(nested_int) == colors.NestedInt
    assert type(copy.copy(nested_int)) == int
    assert type(copy.deepcopy(nested_int)) == int
    assert nested_int == _INT
    assert list(nested_int) == list(_DICT)
    assert nested_int.items() == _DICT.items()
    assert nested_int[42] == 69
    assert nested_int["one"] == 1
    assert pytest.raises(KeyError, lambda: nested_int["42"])


def test_flat_ui_colors():
    assert type(colors.FlatUIColors.turquoise) == int
    assert colors.FlatUIColors.turquoise == 0x1ABC9C


def test_material_colors():
    assert type(colors.MaterialColors.red) == colors.NestedInt
    assert colors.MaterialColors.red == 0xF44336
    assert colors.MaterialColors.red == colors.MaterialColors.red[500]
    assert colors.MaterialColors.red != colors.MaterialColors.red[600]


def test_all_colors():
    assert colors.AllColors.orange is colors.MaterialColors.orange
    assert colors.AllColors.default == 0x00897B
