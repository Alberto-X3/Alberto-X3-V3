__all__ = ("CaseFile",)


from AlbertoX3.database import db, select
from AlbertoX3.naff_wrapper import Extension
from AlbertoX3.translations import TranslationNamespace, t
from AlbertoX3.utils import get_logger
from naff.client.client import Client
from naff.client.const import EMBED_FIELD_VALUE_LENGTH, MISSING
from naff.models.discord.components import ActionRow, Button
from naff.models.discord.embed import Embed, EmbedField
from naff.models.discord.enums import ButtonStyles
from naff.models.discord.modal import Modal, ParagraphText
from naff.models.discord.user import BaseUser
from naff.models.naff.application_commands import OptionTypes, SlashCommandChoice, SlashCommandOption, slash_command
from naff.models.naff.command import check
from naff.models.naff.context import InteractionContext, ModalContext
from ..colors import Colors
from ..db import CaseFileModel
from ..permission import RolePlayPermission


logger = get_logger(__name__)
tg: TranslationNamespace = t.g
t: TranslationNamespace = t.role_play


_CASE_STATUS: dict[int, str] = {
    0: "open",
    1: "active",
    2: "closed",
}


async def rpp_cf_edit_check(ctx: InteractionContext) -> bool:
    if await RolePlayPermission.cf_edit.check_permissions(ctx.author):  # granted by default
        return True

    cf = await CaseFileModel.get_by_id(ctx.kwargs.get("id", 0))
    if cf is None:
        return False

    return cf.author == ctx.author.id


async def rpp_cf_change_status_check(ctx: InteractionContext) -> bool:
    if await rpp_cf_edit_check(ctx):  # granted by default or author
        return True

    cf = await CaseFileModel.get_by_id(ctx.kwargs.get("id", 0))
    if cf is None:
        return False

    return cf.judge == ctx.author.id


class CaseFile(Extension):
    def __init__(self, bot: Client):
        self.cf_accusation_cache: dict[int, str] = {}

    @slash_command(
        "case-file",
        sub_cmd_name="about",
        sub_cmd_description="Basic information about *Case File*",
    )
    async def cf_about(self, ctx: InteractionContext):
        embed = Embed(
            title=t.cf.about.title,
            description=t.cf.about.description.replace("\n", "\n\n"),
            color=Colors.case_file,
        )

        participants: set[int | None] = {None}  # None will be added since fields are nullable
        total = 0  # ID isn't reliable since CF's can be deleted
        participant_fields: set[str] = {
            "author",
            "judge",
            "complainant",
            "defendant",
            "lay_judge",
            "complainant_lawyer",
            "defendant_lawyer",
            "witness",
            "expert",
        }
        async for cf in await db.stream(select(CaseFileModel)):
            participants.update({getattr(cf, p) for p in participant_fields})
            total += 1
        participants.discard(None)

        embed.add_field(
            name=t.cf.about.statistics.title,
            value=t.cf.about.statistics.description(
                case_files=total,
                participants=len(participants),
                last_edited=int((await CaseFileModel.get_last_recent_updated()).last_edited.timestamp()),
                latest_link=self.cf_latest.mention(scope=ctx.guild.id),
            ),
        )

        await ctx.send(embeds=[embed])

    @cf_about.subcommand(
        sub_cmd_name="latest",
        sub_cmd_description="Get the latest *Case file*",
    )
    @RolePlayPermission.cf_view.check
    async def cf_latest(self, ctx: InteractionContext):
        case = await CaseFileModel.get_last_recent_updated()
        title = t.cf.last_recent_title(id=case.id)
        embed = self.get_case_embed(title, case)
        await ctx.send(embeds=[embed])

    @cf_about.subcommand(
        sub_cmd_name="by-id",
        sub_cmd_description="Get a *Case file* by ID",
        options=[
            SlashCommandOption(
                name="id",
                type=OptionTypes.INTEGER,
                description="The ID from the *Case file*",
                required=True,
                min_value=1,
            )
        ],
    )
    @RolePlayPermission.cf_view.check
    async def cf_id(self, ctx: InteractionContext, id: int):  # noqa A002
        case = await CaseFileModel.get_by_id(id)
        if case is not None:
            title = t.cf.title(id=case.id)
            embed = self.get_case_embed(title, case)
        else:
            embed = Embed(
                title=t.cf.not_found.by_id.title(id=id),
                description=t.cf.not_found.by_id.description(id=id),
                color=Colors.case_file,
            )
        await ctx.send(embeds=[embed])

    @cf_about.subcommand(
        sub_cmd_name="create",
        sub_cmd_description="Create a new *Case File*",
        options=[
            SlashCommandOption(name="judge", type=OptionTypes.USER, required=True),
            SlashCommandOption(name="complainant", type=OptionTypes.USER, required=True),
            SlashCommandOption(name="defendant", type=OptionTypes.USER, required=True),
            SlashCommandOption(name="lay_judge", type=OptionTypes.USER, required=False),
            SlashCommandOption(name="complainant_lawyer", type=OptionTypes.USER, required=False),
            SlashCommandOption(name="defendant_lawyer", type=OptionTypes.USER, required=False),
            SlashCommandOption(name="witness", type=OptionTypes.USER, required=False),
            SlashCommandOption(name="expert", type=OptionTypes.USER, required=False),
        ],
    )
    @RolePlayPermission.cf_create.check
    async def cf_create(
        self,
        ctx: InteractionContext,
        judge: BaseUser,
        complainant: BaseUser,
        defendant: BaseUser,
        lay_judge: BaseUser = MISSING,
        complainant_lawyer: BaseUser = MISSING,
        defendant_lawyer: BaseUser = MISSING,
        witness: BaseUser = MISSING,
        expert: BaseUser = MISSING,
    ):
        old_accusation = self.cf_accusation_cache.get(ctx.author.id, MISSING)

        modal = Modal(
            title=t.cf.modal.title,
            custom_id="case.create|accusation",
            components=[
                ParagraphText(
                    label=t.cf.modal.accusation,
                    custom_id="accusation",
                    placeholder=t.cf.modal.placeholder,
                    value=old_accusation,
                    required=True,
                    max_length=EMBED_FIELD_VALUE_LENGTH,
                )
            ],
        )
        await ctx.send_modal(modal)
        m_ctx: ModalContext = await self.bot.wait_for_modal(modal, ctx.author)

        accusation = m_ctx.kwargs["accusation"]
        self.cf_accusation_cache[ctx.author.id] = accusation
        await m_ctx.send(content="```{}```".format(accusation.replace("```", "\u200b``\u200b`")))

        case_kwargs = {
            "author": ctx.author.id,
            "status": 0,
            "judge": judge.id,
            "lay_judge": lay_judge.id,
            "complainant": complainant.id,
            "complainant_lawyer": complainant_lawyer.id,
            "defendant": defendant.id,
            "defendant_lawyer": defendant_lawyer.id,
            "witness": witness.id,
            "expert": expert.id,
            "accusation": accusation,
        }
        preview = CaseFileModel.preview(**case_kwargs)
        preview.id = 0

        components = ActionRow(
            Button(style=ButtonStyles.SUCCESS, label=t.cf.buttons.looks_okay, custom_id="case.create|yes"),
            Button(style=ButtonStyles.DANGER, label=t.cf.buttons.cancel, custom_id="case.create|no"),
        )
        embed = self.get_case_embed(t.cf.title(id=preview.id), preview)

        msg = await ctx.send(embeds=[embed], components=[components])
        c_ctx = (
            await self.bot.wait_for_component(
                messages=[msg],
                components=[components],
                check=lambda event: event.ctx.author.id == ctx.author.id,
            )
        ).ctx
        await c_ctx.defer(edit_origin=True)

        if c_ctx.custom_id == "case.create|yes":
            case = await CaseFileModel.create(**case_kwargs)
            await db.commit()  # to set case.id
            embed = self.get_case_embed(t.cf.title(id=case.id), case)
            components = []
        else:
            for c in components.components:
                c.disabled = True
            components = [components]

        await c_ctx.edit(msg, embeds=[embed], components=components)

    @cf_about.subcommand(
        sub_cmd_name="edit",
        sub_cmd_description="Edit a *Case File*",
        options=[
            SlashCommandOption(
                name="id",
                type=OptionTypes.INTEGER,
                description="The ID from the *Case file*",
                required=True,
                min_value=1,
            )
        ],
    )
    @check(rpp_cf_edit_check)  # type: ignore
    async def cf_edit(self, ctx: InteractionContext, id: int):  # noqa A002
        await ctx.send(tg.coming_soon)

    @cf_about.subcommand(
        sub_cmd_name="change_status",
        sub_cmd_description="Change the status of a *Case File*",
        options=[
            SlashCommandOption(
                name="id",
                type=OptionTypes.INTEGER,
                description="The ID from the *Case file*",
                required=True,
                min_value=1,
            ),
            SlashCommandOption(
                name="status",
                type=OptionTypes.INTEGER,
                description="The new status the *Case File* should have",
                required=True,
                choices=[SlashCommandChoice(name, code) for code, name in _CASE_STATUS.items()],
            ),
        ],
    )
    @check(rpp_cf_edit_check)  # type: ignore
    async def cf_change_status(self, ctx: InteractionContext, id: int, status: int):  # noqa A002
        await ctx.send(tg.coming_soon)

    @staticmethod
    def get_case_embed(title: str, case: CaseFileModel) -> Embed:
        return Embed(
            title=title,
            description=t.cf.description(
                status=getattr(t.cf.status, _CASE_STATUS[case.status]),
                created=int(case.created.timestamp()),
                last_edited=int(case.last_edited.timestamp()),
                author=case.author,
            ),
            fields=[
                # row 1
                EmbedField(  # Judge
                    name=t.cf.case.judge.name,
                    value=t.cf.case.judge.value(judge=case.judge),
                    inline=True,
                ),
                EmbedField(  # Lay Judge
                    name=t.cf.case.lay_judge.name,
                    value=t.cf.case.lay_judge.value(lay_judge=case.lay_judge, cnt=case.lay_judge is not None),
                    inline=True,
                ),
                EmbedField("\u200b", "\u200b", True),
                # row 2
                EmbedField(  # Complainant
                    name=t.cf.case.complainant.name,
                    value=t.cf.case.complainant.value(complainant=case.complainant),
                    inline=True,
                ),
                EmbedField(  # Complainant Lawyer
                    name=t.cf.case.complainant_lawyer.name,
                    value=t.cf.case.complainant_lawyer.value(
                        complainant_lawyer=case.complainant_lawyer, cnt=case.complainant_lawyer is not None
                    ),
                    inline=True,
                ),
                EmbedField("\u200b", "\u200b", True),
                # row 3
                EmbedField(  # Defendant
                    name=t.cf.case.defendant.name,
                    value=t.cf.case.defendant.value(defendant=case.defendant),
                    inline=True,
                ),
                EmbedField(  # Defendant Lawyer
                    name=t.cf.case.defendant_lawyer.name,
                    value=t.cf.case.defendant_lawyer.value(
                        defendant_lawyer=case.defendant_lawyer, cnt=case.defendant_lawyer is not None
                    ),
                    inline=True,
                ),
                EmbedField("\u200b", "\u200b", True),
                # row 4
                EmbedField(  # Witness
                    name=t.cf.case.witness.name,
                    value=t.cf.case.witness.value(witness=case.witness, cnt=case.witness is not None),
                    inline=True,
                ),
                EmbedField(  # Expert
                    name=t.cf.case.expert.name,
                    value=t.cf.case.expert.value(expert=case.expert, cnt=case.expert is not None),
                    inline=True,
                ),
                EmbedField("\u200b", "\u200b", True),
                # row 5
                EmbedField(  # Accusation
                    name=t.cf.case.accusation.name,
                    value=t.cf.case.accusation.value(accusation=case.accusation),
                    inline=False,
                ),
            ],
            color=Colors.case_file,
        )
