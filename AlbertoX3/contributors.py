__all__ = ("Contributor",)


from aenum import NoAliasEnum
from typing import Optional
from .errors import DeveloperArgumentError


_FALSE: frozenset[str] = frozenset(
    {"0", "-1", "none", "nan", "false", "/", "()", "[]", "{}", "set()", "missing", "notset"}
)


class ContributorEnum(NoAliasEnum):
    @property
    def discord_id(self) -> Optional[int]:
        if str(dc_id := self.value[0]).lower() in _FALSE:
            return None
        return int(dc_id)

    @property
    def discord_mention(self) -> Optional[str]:
        return f"<@{self.discord_id}>" if self.discord_id else None

    @property
    def github(self) -> tuple[Optional[int], Optional[str]]:
        if str(gh_raw := self.value[1]).lower() in _FALSE:
            return None, None

        gh_tuple: tuple[str, ...] = tuple(map(str, gh_raw))
        if len(gh_tuple) != 2:
            raise DeveloperArgumentError(
                f"Invalid GitHub ID/Node-ID {gh_tuple!r} for {self.attr}! Expected 'tuple[int, str]'"
            )

        # id processing
        if (gh_id := gh_tuple[0]) not in _FALSE and gh_id.isnumeric():
            gh_id = None
        else:
            gh_id = int(gh_id)

        # node-id processing
        if (gh_node := gh_tuple[1]) in _FALSE:
            gh_node = None

        return gh_id, gh_node

    @property
    def github_id(self) -> Optional[int]:
        return self.github[0]

    @property
    def github_node_id(self) -> Optional[str]:
        return self.github[1]


class Contributor(ContributorEnum):
    # (Discord ID, (GitHub ID, GitHub Node-ID))
    AlbertUnruh = (546320163276849162, (73029826, "MDQ6VXNlcjczMDI5ODI2"))
