from aenum import NoAliasEnum
from typing import Optional

_FALSE: frozenset[str]

class ContributorEnum(NoAliasEnum):
    @property
    def discord_id(self) -> Optional[int]: ...
    @property
    def discord_mention(self) -> Optional[str]: ...
    @property
    def github(self) -> tuple[Optional[int], Optional[str]]: ...
    @property
    def github_id(self) -> Optional[int]: ...
    @property
    def github_node_id(self) -> Optional[str]: ...

class Contributor(ContributorEnum):
    AlbertUnruh: ContributorEnum
