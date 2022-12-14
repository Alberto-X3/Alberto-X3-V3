__all__ = ("CaseFile",)


from AlbertoX3 import get_logger, Extension, t, TranslationNamespace
from naff import (
    Embed,
    EmbedField,
    InteractionContext,
    slash_command,
    SlashCommandOption,
    OptionTypes,
    BaseUser,
    MISSING,
    ModalContext,
    Modal,
    ParagraphText,
    EMBED_FIELD_VALUE_LENGTH,
    Client,
    ActionRow,
    Button,
    ButtonStyles,
)
from .colors import Colors
from .db import CaseFileModel


logger = get_logger(__name__)
tg: TranslationNamespace = t.g
t: TranslationNamespace = t.role_play.case_file  # real type: TranslationDict


_CASE_STATUS: dict[int, str] = {
    0: "open",
    1: "active",
    2: "closed",
}


class CaseFile(Extension):
    def __init__(self, bot: Client):
        self.cf_accusation_cache: dict[int, str] = {}

    @slash_command(
        "case-file",
        sub_cmd_name="about",
        sub_cmd_description="Basic information about *Case File*",
    )
    async def cf_about(self, ctx: InteractionContext):
        embed = Embed(title=t.about.title, description=t.about.description.replace("\n", "\n\n"))
        await ctx.send(embeds=[embed])

    @cf_about.subcommand(sub_cmd_name="latest", sub_cmd_description="Get the latest *Case file*")
    async def cf_latest(self, ctx: InteractionContext):
        case = await CaseFileModel.get_last_recent_updated()
        title = t.last_recent_title(id=case.id)
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
    async def cf_id(self, ctx: InteractionContext, id: int):  # noqa A002
        case = await CaseFileModel.get_by_id(id)
        if case is not None:
            title = t.title(id=case.id)
            embed = self.get_case_embed(title, case)
        else:
            embed = Embed(
                title=t.not_found.by_id.title(id=id),
                description=t.not_found.by_id.description(id=id),
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
            title=t.modal.title,
            custom_id="case.create|accusation",
            components=[
                ParagraphText(
                    label=t.modal.accusation,
                    custom_id="accusation",
                    placeholder=t.modal.placeholder,
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
            Button(style=ButtonStyles.SUCCESS, label=t.buttons.looks_okay, custom_id="case.create|yes"),
            Button(style=ButtonStyles.DANGER, label=t.buttons.cancel, custom_id="case.create|no"),
        )
        embed = self.get_case_embed(t.title(id=preview.id), preview)

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
            embed = self.get_case_embed(t.title(id=case.id), case)
            components = []
        else:
            for c in components.components:
                c.disabled = True
            components = [components]

        await c_ctx.edit(msg, embeds=[embed], components=components)

    @staticmethod
    def get_case_embed(title: str, case: CaseFileModel) -> Embed:
        return Embed(
            title=title,
            description=t.description(
                status=getattr(t.status, _CASE_STATUS[case.status]),
                created=int(case.created.timestamp()),
                last_edited=int(case.last_edited.timestamp()),
                author=case.author,
            ),
            fields=[
                # row 1
                EmbedField(  # Judge
                    name=t.case.judge.name,
                    value=t.case.judge.value(judge=case.judge),
                    inline=True,
                ),
                EmbedField(  # Lay Judge
                    name=t.case.lay_judge.name,
                    value=t.case.lay_judge.value(lay_judge=case.lay_judge, cnt=case.lay_judge is not None),
                    inline=True,
                ),
                EmbedField("\u200b", "\u200b", True),
                # row 2
                EmbedField(  # Complainant
                    name=t.case.complainant.name,
                    value=t.case.complainant.value(complainant=case.complainant),
                    inline=True,
                ),
                EmbedField(  # Complainant Lawyer
                    name=t.case.complainant_lawyer.name,
                    value=t.case.complainant_lawyer.value(
                        complainant_lawyer=case.complainant_lawyer, cnt=case.complainant_lawyer is not None
                    ),
                    inline=True,
                ),
                EmbedField("\u200b", "\u200b", True),
                # row 3
                EmbedField(  # Defendant
                    name=t.case.defendant.name,
                    value=t.case.defendant.value(defendant=case.defendant),
                    inline=True,
                ),
                EmbedField(  # Defendant Lawyer
                    name=t.case.defendant_lawyer.name,
                    value=t.case.defendant_lawyer.value(
                        defendant_lawyer=case.defendant_lawyer, cnt=case.defendant_lawyer is not None
                    ),
                    inline=True,
                ),
                EmbedField("\u200b", "\u200b", True),
                # row 4
                EmbedField(  # Witness
                    name=t.case.witness.name,
                    value=t.case.witness.value(witness=case.witness, cnt=case.witness is not None),
                    inline=True,
                ),
                EmbedField(  # Expert
                    name=t.case.expert.name,
                    value=t.case.expert.value(expert=case.expert, cnt=case.expert is not None),
                    inline=True,
                ),
                EmbedField("\u200b", "\u200b", True),
                # row 5
                EmbedField(  # Accusation
                    name=t.case.accusation.name,
                    value=t.case.accusation.value(accusation=case.accusation),
                    inline=False,
                ),
            ],
            color=Colors.case_file,
        )
