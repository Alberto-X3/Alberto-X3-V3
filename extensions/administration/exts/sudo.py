__all__ = ("Sudo",)


from AlbertoX3.constants import Config
from AlbertoX3.database import redis
from AlbertoX3.environment import OWNER_ID
from AlbertoX3.naff_wrapper import Extension
from AlbertoX3.permission import permission_override
from AlbertoX3.translations import TranslationNamespace, t
from AlbertoX3.utils import get_logger
from naff.api.events.internal import CommandCompletion
from naff.client.client import Client
from naff.models.discord.channel import BaseChannel
from naff.models.naff.application_commands import SlashCommand, slash_command
from naff.models.naff.command import check
from naff.models.naff.context import InteractionContext
from naff.models.naff.listener import listen
from ..permission import AdministrationPermission


logger = get_logger(__name__)
tg: TranslationNamespace = t.g
t: TranslationNamespace = t.administration


@check
async def is_super_user(ctx: InteractionContext) -> bool:
    if ctx.author.id != OWNER_ID:
        return False
    return True


class Sudo(Extension):
    def __init__(self, bot: Client):
        self.s_command_cache: dict[BaseChannel, tuple[SlashCommand, list, dict]] = {}

    @listen()
    async def on_owner_cmd(self, event: CommandCompletion):
        if (ctx := event.ctx).author.id == OWNER_ID:
            self.s_command_cache[event.ctx.channel] = (ctx.command, ctx.args, ctx.kwargs)  # type: ignore

    @slash_command(
        "sudo",
        sub_cmd_name="rerun",
        sub_cmd_description="Activate sudo privileges",
    )
    @is_super_user
    async def s_sudo(self, ctx: InteractionContext):
        if (channel := ctx.channel) not in self.s_command_cache:
            await ctx.send(content=t.s.command_not_in_cache(channel=channel.mention))
            return

        permission_override.set(Config.PERMISSION_LEVELS.max())

        ctx.command, ctx.args, ctx.kwargs = self.s_command_cache[channel]
        ctx.invoke_target = f"{ctx.invoke_target} ({ctx.command.resolved_name})"
        await self.bot._run_slash_command(command=ctx.command, ctx=ctx)  # noqa

    @s_sudo.subcommand(
        sub_cmd_name="clear-cache",
        sub_cmd_description="Clear the bot's cache",
    )
    @AdministrationPermission.s_clear_cache.check
    async def s_clear_cache(self, ctx: InteractionContext):
        await redis.flushdb()
        await ctx.send(t.s.done.cache)

    # reload

    @s_sudo.subcommand(
        sub_cmd_name="stop",
        sub_cmd_description="Stops the bot",
    )
    @AdministrationPermission.s_stop.check
    async def s_stop(self, ctx: InteractionContext):
        await ctx.send(t.s.done.stopping)
        await self.bot.stop()

    @s_sudo.subcommand(
        sub_cmd_name="kill",
        sub_cmd_description="Kills the bot",
    )
    @AdministrationPermission.s_kill.check
    async def s_kill(self, ctx: InteractionContext):
        await ctx.send(t.s.done.killing)
        __import__("sys").exit(1)
