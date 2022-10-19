from typing import Iterator, ItemsView

class NestedInt(int):
    _values: dict[str | int, int]
    def __new__(cls, x: int, values: dict[str | int, int]) -> NestedInt: ...
    def __getitem__(self, item: str | int) -> int: ...
    def __iter__(self) -> Iterator[int]: ...
    def items(self) -> ItemsView[int]: ...
    def __copy__(self) -> int: ...
    def __deepcopy__(self, *_) -> int: ...

_color_data_flat_ui: dict[str, int]
_color_data_material: dict[str, dict[str | int, int]]

def _load_flat_ui(name: str) -> int: ...
def _load_material(name: str) -> NestedInt: ...

class FlatUIColors:
    turquoise: int
    greensea: int
    emerland: int
    nephritis: int
    peterriver: int
    belizehole: int
    amethyst: int
    wisteria: int
    wetasphalt: int
    midnightblue: int
    sunflower: int
    orange: int
    carrot: int
    pumpkin: int
    alizarin: int
    pomegranate: int
    clouds: int
    silver: int
    concrete: int
    asbestos: int

class MaterialColors:
    red: NestedInt
    pink: NestedInt
    purple: NestedInt
    deeppurple: NestedInt
    indigo: NestedInt
    blue: NestedInt
    lightblue: NestedInt
    cyan: NestedInt
    teal: NestedInt
    green: NestedInt
    lightgreen: NestedInt
    lime: NestedInt
    yellow: NestedInt
    amber: NestedInt
    orange: NestedInt
    deeporange: NestedInt
    brown: NestedInt
    grey: NestedInt
    bluegrey: NestedInt

    default: int
    error: int
    warning: int
    assertion: int
    notimplemented: int

    blurple: int
    blurple_legacy: int

    albertunruh: int

class AllColors(FlatUIColors, MaterialColors):
    orange: NestedInt
