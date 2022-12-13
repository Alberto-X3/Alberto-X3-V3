__all__ = ("Moderation",)


from AlbertoX3 import get_logger, Extension
from datetime import datetime, timezone
from datetimeparser import parse
from naff import InteractionContext, Member, OptionTypes, SlashCommandOption, slash_command
from .db import BanModel, UnbanModel, KickModel, MuteModel, UnmuteModel, DeleteModel


logger = get_logger(__name__)


class Moderation(Extension):
    @slash_command(
        "ban",
        description="Wields the ban-hammer",
        options=[
            SlashCommandOption(
                name="user",
                description="The user to hit with the ban-hammer",
                required=True,
                autocomplete=False,
                type=OptionTypes.USER,
            ),
            SlashCommandOption(
                name="reason",
                description="Why you want to wield the ban-hammer",
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
    async def ban(
        self, ctx: InteractionContext, *, user: Member, reason: str | None = None, duration: str | None = None
    ):
        if reason is None:
            reason = "NO REASON -- REPLACE THIS WITH TRANSLATION"

        until: datetime | None = None
        if duration is not None:
            parsed = parse(duration, "utc").time
            utc = datetime.utcnow()  # don't use utils.get_utcnow since parse doesn't set tzinfo
            if parsed > utc:  # in the future
                until = parsed.replace(tzinfo=timezone.utc)

        logger.warning(f"{__name__}.Moderation.ban has no actual functionality!")
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
        "unban",
        description="Takes away the ban-hammer",
        options=[
            SlashCommandOption(
                name="user",
                description="The user to take away the ban-hammer",
                required=True,
                autocomplete=False,
                type=OptionTypes.USER,
            ),
            SlashCommandOption(
                name="reason",
                description="Why you want to take away the ban-hammer",
                required=False,
                autocomplete=False,
                type=OptionTypes.STRING,
                max_length=128,
            ),
        ],
    )
    async def unban(self, ctx: InteractionContext, *, user: Member, reason: str | None = None):
        if reason is None:
            reason = "NO REASON -- REPLACE THIS WITH TRANSLATION"

        logger.warning(f"{__name__}.Moderation.unban has no actual functionality!")
        await UnbanModel.add(
            member=user.id,
            executor=ctx.author.id,
            reason=reason,
        )

        await ctx.send(f"Unbanned ``{user.tag}`` with reason ``{reason}``")

    @slash_command(
        "kick",
        description="Wields the kick-stick",
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
        await KickModel.add(
            member=user.id,
            executor=ctx.author.id,
            reason=reason,
        )

        await ctx.send(f"Kicked ``{user.tag}`` with reason ``{reason}``")

    @slash_command(
        "mute",
        description="Throws the mute-axe",
        options=[
            SlashCommandOption(
                name="user",
                description="The user to hit with the mute-axe",
                required=True,
                autocomplete=False,
                type=OptionTypes.USER,
            ),
            SlashCommandOption(
                name="reason",
                description="Why you want to wield the mute-axe",
                required=False,
                autocomplete=False,
                type=OptionTypes.STRING,
                max_length=128,
            ),
            SlashCommandOption(
                name="duration",
                description="Until when the user shall never be heard (ISO/english description)",
                required=False,
                autocomplete=False,
                type=OptionTypes.STRING,
            ),
        ],
    )
    async def mute(
        self, ctx: InteractionContext, *, user: Member, reason: str | None = None, duration: str | None = None
    ):
        if reason is None:
            reason = "NO REASON -- REPLACE THIS WITH TRANSLATION"

        until: datetime | None = None
        if duration is not None:
            parsed = parse(duration, "utc").time
            utc = datetime.utcnow()  # don't use utils.get_utcnow since parse doesn't set tzinfo
            if parsed > utc:  # in the future
                until = parsed.replace(tzinfo=timezone.utc)

        logger.warning(f"{__name__}.Moderation.mute has no actual functionality!")
        await MuteModel.add(
            member=user.id,
            executor=ctx.author.id,
            reason=reason,
            until=until,
        )

        if until:
            info = f"(until <t:{int(until.timestamp())}:f>)"
        else:
            info = "(permanently)"

        await ctx.send(f"Muted ``{user.tag}`` with reason ``{reason}`` {info}")

    @slash_command(
        "unmute",
        description="Takes away the mute-axe",
        options=[
            SlashCommandOption(
                name="user",
                description="The user to take away the mute-axe",
                required=True,
                autocomplete=False,
                type=OptionTypes.USER,
            ),
            SlashCommandOption(
                name="reason",
                description="Why you want to take away the mute-axe",
                required=False,
                autocomplete=False,
                type=OptionTypes.STRING,
                max_length=128,
            ),
        ],
    )
    async def unmute(self, ctx: InteractionContext, *, user: Member, reason: str | None = None):
        if reason is None:
            reason = "NO REASON -- REPLACE THIS WITH TRANSLATION"

        logger.warning(f"{__name__}.Moderation.unmute has no actual functionality!")
        await UnmuteModel.add(
            member=user.id,
            executor=ctx.author.id,
            reason=reason,
        )

        await ctx.send(f"Unmuted ``{user.tag}`` with reason ``{reason}``")

    @slash_command(
        "delete",
        description="Takes out the eraser",
        options=[
            SlashCommandOption(
                name="amount",
                description="How many messages to wipe out",
                required=True,
                autocomplete=False,
                type=OptionTypes.INTEGER,
                min_value=1,
                max_value=128,
            ),
            SlashCommandOption(
                name="user",
                description="The user to wipe out from chat",
                required=False,
                autocomplete=False,
                type=OptionTypes.USER,
            ),
        ],
    )
    async def delete(self, ctx: InteractionContext, *, amount: int, user: Member | None = None):
        logger.warning(f"{__name__}.Moderation.delete has no actual functionality!")
        await DeleteModel.add(
            amount=amount,
            channel=ctx.channel.id,
            executor=ctx.author.id,
            user=user.id,
        )

        if user is not None:
            info = user.tag
        else:
            info = "@everyone"

        await ctx.send(f"Deleted ``{amount}`` messages from ``{info}``")
