__all__ = ("FileCase",)


from AlbertoX3 import get_logger, Extension, t, TranslationNamespace
from naff import Embed, EmbedField, InteractionContext, slash_command
from .colors import Colors
from .db import FileCaseModel


logger = get_logger(__name__)
tg: TranslationNamespace = t.g
t: TranslationNamespace = t.role_play.file_case  # real type: TranslationDict


class FileCase(Extension):
    @slash_command(
        "file-case",
        description="Basic information about *File Case*",
    )
    async def fc_info(self, ctx: InteractionContext):
        case = await FileCaseModel.get_last_recent_updated()
        embed = Embed(
            title=t.last_recent_title(id=case.id),
            description=t.description(
                created=int(case.created.timestamp()),
                last_edited=int(case.last_edited.timestamp()),
                author=case.author,
            ),
            fields=[
                EmbedField(  # Judge
                    name=t.case.judge.name,
                    value=t.case.judge.value(judge=case.judge),
                    inline=True,
                ),
                EmbedField(  # Complainant
                    name=t.case.complainant.name,
                    value=t.case.complainant.value(complainant=case.complainant),
                    inline=True,
                ),
                EmbedField(  # Defendant
                    name=t.case.defendant.name,
                    value=t.case.defendant.value(defendant=case.defendant),
                    inline=True,
                ),
                EmbedField(  # Appeal
                    name=t.case.appeal.name,
                    value=t.case.appeal.value(appeal=case.appeal),
                    inline=False,
                ),
            ],
            color=Colors.file_case,
        )
        await ctx.send(embeds=[embed])
