"""Allow communication between bots.

Following rules have to be followed for a flawless communication:
1.  The message has to be built as follows:
        origin>>BOT-ID
        target>>BOT-ID-1
        target>>BOT-ID-2
        ...
        target>>BOT-ID-n
        endpoint>>ENDPOINT-TO-INTERACT-WITH
        JSON-FORMATTED-CONTENT
    Notes:
        - you have to replace everything in CAPS with actual values
        - only optional argument is ``origin`` and will default to the author
          - ``origin`` has to be enabled for bots to use it -> set ``ALLOW_BOT_ORIGIN`` to ``True``
        - ``target`` can be set multiple times to target multiple bots
        - if JSON-FORMATTED-CONTENT is empty it can either be represented by ``{}`` or the end of line
2.  The message can either be sent as the message content or attached as
    a file (for that to work there can't be any contents in the message)


#######

THIS FILE IS INTENDED TO BE COPY-PASTED
IN DIFFERENT PROJECTS TO ENSURE FLAWLESS
COMMUNICATION FROM THE API ITSELF!

PLEASE LET THE FILE AS IT IS!!!
*The latest version can be found [here](https://github.com/Alberto-X3/Alberto-X3-V3/blob/develop/AlbertoX3/bot_api.py)*

> Feels free to contribute and enhance the protocol on GitHub (link can be found above)!

Requirements:
    The only true requirements are ``attrs`` to define the class ``Argument`` and to download attachments.
    Besides that ``orjson`` is suggested for faster json-operations, but it falls back to ``json`` if not installed.
    Additionally, ``naff`` is used in here just for type-hinting, but a fallback-implementation is provided.

NOTE:
    MAY HAVE COMPATIBILITY ISSUES WITH OTHER LIBRARIES THAN ``naff``!
    If you encounter any issues be sure to submit them:
        https://bit.ly/AlbertoX3-BotAPI-Incompatible


LAST-EDITED: 2023.01.02  # YYYY.MM.DD
API-VERSION: 1  # current protocol-version  # won't be send in requests atm

Copyright 2022-present (c) AlbertUnruh - Alberto-X3
"""
__all__ = (
    "BOT_API_VERSION",
    "Argument",
    "get_arguments",
    "create_arguments",
    "send_arguments",
)


import aiohttp
import attrs
import re
import typing
from io import StringIO

try:
    from orjson import loads, dumps
except ModuleNotFoundError:
    from json import loads, dumps
try:
    from naff import Client, Message
    from naff.client.mixins.send import SendMixin
except ModuleNotFoundError:
    # maybe other libraries like Discord.py are installed -> manual type-hinting
    class Attachment:
        url: str

    class Author:
        bot: bool
        id: int  # noqa A003

    class Client:
        user: Author

    class Message:
        attachments: list[Attachment]
        author: Author
        content: str

    class SendMixin:
        async def send(self, content: str, files: list[StringIO], *_, **__):  # noqa ANN002, ANN003, ANN201
            pass


ALLOW_ORIGIN: bool = False
"""Whether bots can set ``origin`` or not"""
MAX_MESSAGE_CONTENT_SIZE: int = 2000
"""How long a message can be before it's moved into a file"""
BOT_API_VERSION: str = re.search(r"^API-VERSION:\s*(\S+)\s*(#.*)?$", __doc__, re.MULTILINE).group(1)
"""The version of the bot-api"""

_ARGUMENT_VALIDATOR_REGEX: re.Pattern[str] = re.compile(
    r"^(origin>>\d+\n)?(target>>\d+\n)+endpoint>>.+(\n\{(.|\n)*}|)$"
)
"""A RegEx to validate the input for right argument order etc"""


@attrs.define(
    repr=True,
    hash=False,
    init=True,
    slots=True,
    frozen=True,
    kw_only=True,
    eq=False,
    order=False,
)
class Argument:
    author: int
    """The author who send the request to the API"""
    origin: int
    """The origin of the request (equals author unless someone send a modified request"""
    targets: list[int]
    """The targets for the request"""
    endpoint: str
    """The endpoint for the request"""
    content: dict
    """The contents of the message or file if the message is empty"""

    @classmethod
    async def from_message(cls, message: Message) -> "Argument":
        if not (data := message.content):
            file = message.attachments[0]
            async with aiohttp.client.ClientSession() as session:
                response = await session.get(file.url)
                data = await response.text("utf-8")

        if _ARGUMENT_VALIDATOR_REGEX.match(data) is None:
            raise ValueError(f"Data {data!r} is wrong configured!")

        author = message.author.id
        origin = author
        targets = []
        endpoint = ""
        json = ""
        for line in data.splitlines(keepends=False):
            if not line.startswith("{") and not json:
                argument, value = line.split(">>")
                match argument:
                    case "origin":
                        if not (message.author.bot is True and ALLOW_ORIGIN is False):
                            origin = int(value)
                    case "target":
                        targets.append(int(value))
                    case "endpoint":
                        endpoint = value
            else:
                json += f"{line}\n"
        json = json.strip("\n") or "{}"
        try:
            content = loads(json)
        except ValueError as e:
            raise ValueError(f"Invalid JSON {json!r}!") from e

        return cls(author=author, origin=origin, targets=targets, endpoint=endpoint, content=content)

    @classmethod
    def create(
        cls, client: Client, targets: list[int | typing.SupportsInt], endpoint: str, content: dict
    ) -> "Argument":
        author = client.user.id
        return cls(
            author=int(author),
            origin=int(author),
            targets=list(map(int, targets)),
            endpoint=endpoint,
            content=content,
        )


async def get_arguments(message: Message) -> Argument:
    return await Argument.from_message(message)


def create_arguments(client: Client, targets: list[int | typing.SupportsInt], endpoint: str, content: dict) -> Argument:
    return Argument.create(client, targets, endpoint, content)


async def send_arguments(*, argument: Argument, client: Client, channel: SendMixin) -> typing.NoReturn:
    content = f"origin>>{client.user.id}\n"
    content += "".join(f"target>>{target}\n" for target in argument.targets)
    content += f"endpoint>>{argument.endpoint}\n"
    if isinstance(c := dumps(argument.content), bytes):
        c = c.decode("utf-8")
    content += c
    if len(content) > MAX_MESSAGE_CONTENT_SIZE:
        file = StringIO(content)
        file.name = f"{argument.endpoint}-request-from-{client.user.id}.txt"
        await channel.send(files=[file])
    else:
        await channel.send(content=content)
