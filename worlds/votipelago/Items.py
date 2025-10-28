import typing

from BaseClasses import Item, ItemClassification
from typing import Dict, List

PROGRESSION = ItemClassification.progression
PROGRESSION_SKIP_BALANCING = ItemClassification.progression_skip_balancing
USEFUL = ItemClassification.useful
FILLER = ItemClassification.filler


class ItemData(typing.NamedTuple):
    code: typing.Optional[int]
    classification: ItemClassification


item_table: Dict[str, ItemData] = {
    # Progressive Items
    "Progressive Poll Key": ItemData(1, PROGRESSION),
    "Letter V": ItemData(2, PROGRESSION_SKIP_BALANCING),
    "Letter O": ItemData(3, PROGRESSION_SKIP_BALANCING),
    "Letter T": ItemData(4, PROGRESSION_SKIP_BALANCING),
    "Letter I": ItemData(5, PROGRESSION_SKIP_BALANCING),
    "Letter P": ItemData(6, PROGRESSION_SKIP_BALANCING),
    "Letter E": ItemData(7, PROGRESSION_SKIP_BALANCING),
    "Letter L": ItemData(8, PROGRESSION_SKIP_BALANCING),
    "Letter A": ItemData(9, PROGRESSION_SKIP_BALANCING),
    "Letter G": ItemData(10, PROGRESSION_SKIP_BALANCING),

    # Useful Items
    "Major Time Skip": ItemData(11, USEFUL),

    # Filler Items
    "Minor Time Skip": ItemData(12, FILLER),

    # Event Items
    "Votipelago Victory": ItemData(None, PROGRESSION)

}