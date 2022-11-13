__all__ = ("Automation",)


import re
from AlbertoX3 import get_logger, Extension, Config, t, TranslationNamespace
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
            embed.color = Colors.automation
            requirements = []
            for req in parse_requirements("requirements.txt", PipSession()):
                requirement = _LIB_NAME_REGEX.search(req.requirement).group(2)
                version = _LIB_VERSION_REGEX.search(req.requirement).group(2)
                # ToDo: actually check whether it's the latest version
                requirements.append(t.requirements.ok(requirement=requirement, version=version))
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
