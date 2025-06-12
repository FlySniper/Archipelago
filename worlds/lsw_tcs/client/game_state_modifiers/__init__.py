import abc
from typing import Container

from ..type_aliases import TCSContext


class ItemReceiver(abc.ABC):
    @property
    @abc.abstractmethod
    def receivable_ap_ids(self) -> Container[int]: ...

    @abc.abstractmethod
    async def update_game_state(self, ctx: TCSContext) -> None: ...
