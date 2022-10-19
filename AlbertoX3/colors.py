__all__ = (
    "AllColors",
    "FlatUIColors",
    "MaterialColors",
)


from yaml import safe_load
from .constants import LIB_PATH


class NestedInt(int):
    """
    Integer with a read-only dictionary.
    """

    def __new__(cls, x, values):
        self = super().__new__(cls, x)
        self._values = values
        return self

    def __getitem__(self, item):
        return self._values[item]

    def __iter__(self):
        return self._values.__iter__()

    def items(self):
        return self._values.items()

    def __copy__(self):
        return int(self)

    def __deepcopy__(self, *_):
        return int(self)


_color_data_flat_ui = safe_load(LIB_PATH.joinpath("colors/flat_ui.yml").read_text("utf-8"))
_color_data_material = safe_load(LIB_PATH.joinpath("colors/material.yml").read_text("utf-8"))


def _load_flat_ui(name):
    return _color_data_flat_ui[name]


def _load_material(name):
    data = _color_data_material[name]
    return NestedInt(data[500], data)


class FlatUIColors:
    """
    All Flat-UI-Colors (https://materialui.co/flatuicolors).
    """

    __slots__ = ()

    turquoise = _load_flat_ui("turquoise")
    greensea = _load_flat_ui("greensea")
    emerland = _load_flat_ui("emerland")
    nephritis = _load_flat_ui("nephritis")
    peterriver = _load_flat_ui("peterriver")
    belizehole = _load_flat_ui("belizehole")
    amethyst = _load_flat_ui("amethyst")
    wisteria = _load_flat_ui("wisteria")
    wetasphalt = _load_flat_ui("wetasphalt")
    midnightblue = _load_flat_ui("midnightblue")
    sunflower = _load_flat_ui("sunflower")
    orange = _load_flat_ui("orange")
    carrot = _load_flat_ui("carrot")
    pumpkin = _load_flat_ui("pumpkin")
    alizarin = _load_flat_ui("alizarin")
    pomegranate = _load_flat_ui("pomegranate")
    clouds = _load_flat_ui("clouds")
    silver = _load_flat_ui("silver")
    concrete = _load_flat_ui("concrete")
    asbestos = _load_flat_ui("asbestos")


class MaterialColors:
    """
    All Material-Colors (https://materialui.co/colors).
    """

    __slots__ = ()

    red = _load_material("red")
    pink = _load_material("pink")
    purple = _load_material("purple")
    deeppurple = _load_material("deeppurple")
    indigo = _load_material("indigo")
    blue = _load_material("blue")
    lightblue = _load_material("lightblue")
    cyan = _load_material("cyan")
    teal = _load_material("teal")
    green = _load_material("green")
    lightgreen = _load_material("lightgreen")
    lime = _load_material("lime")
    yellow = _load_material("yellow")
    amber = _load_material("amber")
    orange = _load_material("orange")
    deeporange = _load_material("deeporange")
    brown = _load_material("brown")
    grey = _load_material("grey")
    bluegrey = _load_material("bluegrey")

    default = teal[600]
    error = red["a700"]
    warning = yellow["a200"]
    assertion = orange[900]
    notimplemented = lightblue[900]

    blurple = 0x5865F2
    blurple_legacy = 0x7289DA

    albertunruh = 0x3C62F9


class AllColors(FlatUIColors, MaterialColors):
    """
    Flat-UI-Colors and Material-Colors combined.

    Notes
    -----
    There is a name-conflict with ``orange``. The value from ``MaterialColors`` will be set since it's more detailed.
    """

    # in case I want to change something about the empty __slots__
    __slots__ = FlatUIColors.__slots__ + MaterialColors.__slots__  # value: ()

    orange = MaterialColors.orange
