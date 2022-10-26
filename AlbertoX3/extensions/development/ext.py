__all__ = ("Debug",)


from AlbertoX3 import get_logger, get_value_table, Config
from io import StringIO
from naff import Extension, InteractionContext, File
from naff.ext.debug_extension import DebugExtension


logger = get_logger(__name__)


class Debug(DebugExtension, Extension):
    @DebugExtension.debug_info.subcommand("config", sub_cmd_description="Get information about the config")
    async def config_info(self, ctx: InteractionContext) -> None:
        f = File(file=StringIO(get_value_table(Config)), file_name="config.log")

        await ctx.send(files=f)
