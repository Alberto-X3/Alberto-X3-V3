__all__ = ("Moderation",)


from AlbertoX3 import get_logger
from datetime import datetime, timezone
from datetimeparser import parse
from naff import Extension, InteractionContext, Member, OptionTypes, SlashCommandOption, slash_command
from .db import BanModel, KickModel


logger = get_logger(__name__)


class Moderation(Extension):
    @slash_command(
        "ban",
        description="Wields the banhammer",
        options=[
            SlashCommandOption(
                name="user",
                description="The user to hit with the banhammer",
                required=True,
                autocomplete=False,
                type=OptionTypes.USER,
            ),
            SlashCommandOption(
                name="reason",
                description="Why you want to wield the banhammer",
                required=False,
                autocomplete=False,
                type=OptionTypes.STRING,
                max_length=128,
            ),
            SlashCommandOption(
                name="duration",
                description="Until when the user shall vanish (ISO/english description)",
                required=False,
                autocomplete=False,
                type=OptionTypes.STRING,
            ),
        ],
    )
    async def ban(self, ctx: InteractionContext, *, user: Member, reason: str | None = None, duration: str | None):
        if reason is None:
            reason = "NO REASON -- REPLACE THIS WITH TRANSLATION"

        until: datetime | None = None
        if duration is not None:
            parsed = parse(duration, "utc")
            utc = datetime.utcnow()  # don't use utils.get_utcnow since parse doesn't set tzinfo
            if parsed > utc:  # in the future
                until = parsed.replace(tzinfo=timezone.utc)

        logger.warning(f"{__name__}.Moderation.ban has no actual functionality!")
        from AlbertoX3.database import db_context

        async with db_context():
            await BanModel.add(
                member=user.id,
                executor=ctx.author.id,
                reason=reason,
                until=until,
            )

        if until:
            info = f"(until <t:{int(until.timestamp())}:f>)"
        else:
            info = "(permanently)"

        await ctx.send(f"Banned ``{user.tag}`` with reason ``{reason}`` {info}")

    @slash_command(
        "kick",
        description="Wields the lame kick-stick",
        options=[
            SlashCommandOption(
                name="user",
                description="The user to hit with the kick-stick",
                required=True,
                autocomplete=False,
                type=OptionTypes.USER,
            ),
            SlashCommandOption(
                name="reason",
                description="Why you want to wield the kick-stick",
                required=False,
                autocomplete=False,
                type=OptionTypes.STRING,
                max_length=128,
            ),
        ],
    )
    async def kick(self, ctx: InteractionContext, *, user: Member, reason: str | None = None):
        if reason is None:
            reason = "NO REASON -- REPLACE THIS WITH TRANSLATION"

        logger.warning(f"{__name__}.Moderation.kick has no actual functionality!")
        from AlbertoX3.database import db_context

        async with db_context():
            await KickModel.add(
                member=user.id,
                executor=ctx.author.id,
                reason=reason,
            )

        await ctx.send(f"Kicked ``{user.tag}`` with reason ``{reason}``")
