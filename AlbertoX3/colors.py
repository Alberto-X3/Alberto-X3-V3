__all__ = (
    "AllColors",
    "FlatUIColors",
    "MaterialColors",
)


from typing import Any, ItemsView, Iterator
from yaml import safe_load
from .constants import LIB_PATH


class NestedInt(int):
    """
    Integer with a read-only dictionary.
    """

    _values: dict[str | int, int]

    def __new__(cls, x: int, values: dict[str | int, int]):
        self = super().__new__(cls, x)
        self._values = values
        return self

    def __getitem__(self, item: str | int) -> int:
        return self._values[item]

    def __iter__(self) -> Iterator[int]:
        return self._values.__iter__()

    def items(self) -> ItemsView:
        return self._values.items()

    def __copy__(self) -> int:
        return int(self)

    def __deepcopy__(self, *_: Any) -> int:
        return int(self)


_color_data_flat_ui: dict[str, int]
_color_data_flat_ui = safe_load(LIB_PATH.joinpath("colors/flat_ui.yml").read_text("utf-8"))
_color_data_material: dict[str, dict[str | int, int]]
_color_data_material = safe_load(LIB_PATH.joinpath("colors/material.yml").read_text("utf-8"))


def _load_flat_ui(name: str) -> int:
    return _color_data_flat_ui[name]


def _load_material(name: str) -> NestedInt:
    data = _color_data_material[name]
    return NestedInt(data[500], data)


class FlatUIColors:
    """
    All Flat-UI-Colors (https://materialui.co/flatuicolors).
    """

    __slots__ = ()

    turquoise: int = _load_flat_ui("turquoise")
    greensea: int = _load_flat_ui("greensea")
    emerland: int = _load_flat_ui("emerland")
    nephritis: int = _load_flat_ui("nephritis")
    peterriver: int = _load_flat_ui("peterriver")
    belizehole: int = _load_flat_ui("belizehole")
    amethyst: int = _load_flat_ui("amethyst")
    wisteria: int = _load_flat_ui("wisteria")
    wetasphalt: int = _load_flat_ui("wetasphalt")
    midnightblue: int = _load_flat_ui("midnightblue")
    sunflower: int = _load_flat_ui("sunflower")
    orange: int = _load_flat_ui("orange")
    carrot: int = _load_flat_ui("carrot")
    pumpkin: int = _load_flat_ui("pumpkin")
    alizarin: int = _load_flat_ui("alizarin")
    pomegranate: int = _load_flat_ui("pomegranate")
    clouds: int = _load_flat_ui("clouds")
    silver: int = _load_flat_ui("silver")
    concrete: int = _load_flat_ui("concrete")
    asbestos: int = _load_flat_ui("asbestos")


class MaterialColors:
    """
    All Material-Colors (https://materialui.co/colors).
    """

    __slots__ = ()

    red: NestedInt = _load_material("red")
    pink: NestedInt = _load_material("pink")
    purple: NestedInt = _load_material("purple")
    deeppurple: NestedInt = _load_material("deeppurple")
    indigo: NestedInt = _load_material("indigo")
    blue: NestedInt = _load_material("blue")
    lightblue: NestedInt = _load_material("lightblue")
    cyan: NestedInt = _load_material("cyan")
    teal: NestedInt = _load_material("teal")
    green: NestedInt = _load_material("green")
    lightgreen: NestedInt = _load_material("lightgreen")
    lime: NestedInt = _load_material("lime")
    yellow: NestedInt = _load_material("yellow")
    amber: NestedInt = _load_material("amber")
    orange: NestedInt = _load_material("orange")
    deeporange: NestedInt = _load_material("deeporange")
    brown: NestedInt = _load_material("brown")
    grey: NestedInt = _load_material("grey")
    bluegrey: NestedInt = _load_material("bluegrey")


class AllColors(FlatUIColors, MaterialColors):
    """
    Flat-UI-Colors and Material-Colors combined.

    Notes
    -----
    There is a name-conflict with ``orange``. The value from ``MaterialColors`` will be set since it's more detailed.
    """

    # in case I want to change something about the empty __slots__
    __slots__ = FlatUIColors.__slots__ + MaterialColors.__slots__  # value: ()

    orange: NestedInt = MaterialColors.orange

    default: int = MaterialColors.teal[600]
    error: int = MaterialColors.red["a700"]
    warning: int = MaterialColors.yellow["a200"]
    assertion: int = MaterialColors.orange[900]
    notimplemented: int = MaterialColors.lightblue[900]

    blurple: int = 0x5865F2
    blurple_legacy: int = 0x7289DA

    albertunruh: int = 0x3C62F9
