__all__ = ("Automation",)


import orjson
import re
from aiohttp.client import ClientSession
from AlbertoX3 import get_logger, Extension, Config, t, TranslationNamespace
from importlib.metadata import Distribution, PackageNotFoundError
from naff import (
    InteractionContext,
    Task,
    TimeTrigger,
    slash_command,
    Embed,
    EmbedFooter,
    Listener,
)
from .colors import Colors


logger = get_logger(__name__)
tg: TranslationNamespace = t.g
t: TranslationNamespace = t.automation

_LIB_NAME_REGEX: re.Pattern[str] = re.compile(r"(^|#egg=)(?!git\+)([a-zA-Z.,_\-\[\]]+)")
_LIB_VERSION_REGEX: re.Pattern[str] = re.compile(r"((?<!egg)=|@)([\w.]+)#?")
_GITHUB_CORE_REGEX: re.Pattern[str] = re.compile(r"github\.com/(\S+/\S+)\.git")


class Automation(Extension):
    @slash_command(
        "auto",
        sub_cmd_name="check",
        sub_cmd_description="Checks for updates for everything automated",
    )
    async def check(self, ctx: InteractionContext):
        embed = Embed(t.update_check.title)
        embed.footer = EmbedFooter(
            tg.executed_by(user=ctx.author.tag, id=ctx.author.id), icon_url=ctx.author.avatar.url
        )
        try:
            from pip._internal.req import parse_requirements  # noqa
            from pip._internal.network.session import PipSession  # noqa
        except ModuleNotFoundError:
            embed.color = Colors.error
            embed.description = t.not_installed(lib="pip")
        else:
            pip_session = PipSession()
            async with ClientSession() as http_session:

                embed.color = Colors.automation
                requirements = []
                for req in parse_requirements("requirements.txt", pip_session):
                    requirement = _LIB_NAME_REGEX.search(req.requirement).group(2)
                    version = _LIB_VERSION_REGEX.search(req.requirement).group(2)

                    if "." in version:  # something like 1.2.3 -> version on PyPI
                        response = await http_session.get(f"https://pypi.org/pypi/{requirement}/json")
                        metadata = await response.json(loads=orjson.loads)
                        latest = metadata["info"]["version"]
                        req_kwargs = {"requirement": requirement, "version": version}

                        if version == latest:
                            requirements.append(t.requirements.ok(**req_kwargs))
                        else:
                            requirements.append(t.requirements.old(**req_kwargs, new_version=latest))

                    else:  # something like dev -> branch on GitHub
                        core = _GITHUB_CORE_REGEX.search(req.requirement).group(1)
                        response = await http_session.get(f"https://api.github.com/repos/{core}/commits/{version}")
                        metadata = await response.json(loads=orjson.loads)
                        latest = metadata["sha"]

                        try:
                            dist = Distribution.from_name(core.split("/")[-1])
                        except PackageNotFoundError:
                            requirements.append(
                                t.requirements.unknown_gh(requirement=requirement, branch=version, new_sha=latest[:7])
                            )
                        else:
                            metadata = orjson.loads(dist.read_text("direct_url.json"))
                            sha = metadata["vcs_info"]["commit_id"]

                            req_kwargs = {"requirement": requirement, "branch": version, "sha": sha[:7]}
                            if sha == latest:
                                requirements.append(t.requirements.ok_gh(**req_kwargs))
                            else:
                                requirements.append(t.requirements.old_gh(**req_kwargs, new_sha=latest[:7]))

                embed.description = "\n".join(requirements)

        await ctx.send(embeds=[embed])

    @Task.create(trigger=TimeTrigger(hour=Config.AUTO_HOUR, minute=Config.AUTO_MINUTE, seconds=Config.AUTO_SECOND))
    async def auto_check(self):
        client = self.bot
        channel = await self.bot.fetch_channel(Config.AUTO_CHANNEL)
        guild = channel.guild
        author = guild.me
        ctx = InteractionContext(  # noqa S106
            client=client,
            author=author,
            guild_id=guild.id,
            channel=channel,
            context_type=2,
            interaction_id=0,
            token="",
        )
        ctx.send = channel.send
        await self.check(ctx)

    @Listener.create("startup")
    async def startup_check(self):
        await self.auto_check()
