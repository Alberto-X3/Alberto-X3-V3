__all__ = ("FileCase",)


from AlbertoX3 import get_logger, Extension, t, TranslationNamespace
from naff import Embed, EmbedField, InteractionContext, slash_command
from .colors import Colors
from .db import FileCaseModel


logger = get_logger(__name__)
tg: TranslationNamespace = t.g
t: TranslationNamespace = t.role_play.file_case  # real type: TranslationDict


_CASE_STATUS: dict[int, str] = {
    0: "open",
    1: "active",
    2: "closed",
}


class FileCase(Extension):
    @slash_command(
        "file-case",
        description="Basic information about *File Case*",
    )
    async def fc_info(self, ctx: InteractionContext):
        case = await FileCaseModel.get_last_recent_updated()
        title = t.last_recent_title(id=case.id)
        embed = self.get_case_embed(title, case)
        await ctx.send(embeds=[embed])

    @staticmethod
    def get_case_embed(title: str, case: FileCaseModel) -> Embed:
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
            color=Colors.file_case,
        )
