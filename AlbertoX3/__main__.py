from AlbertoX3 import *
from AlbertUnruhUtils.utils.logger import get_logger
from naff import Client, Intents


logger = get_logger(None, level=LOG_LEVEL)

# naff debugger
__import__("naff").logger.setLevel("INFO")  # don't need naff in namespace

# asyncio debugger
if isinstance(LOG_LEVEL, int) or LOG_LEVEL.isnumeric():
    event_loop.set_debug(int(LOG_LEVEL) <= 10)
else:
    event_loop.set_debug(LOG_LEVEL in {"DEBUG", "NOTSET"})
if event_loop.get_debug():
    logger.warning("asyncio is in debug-mode")


Config(LIB_PATH.parent.joinpath("config.alberto-x3.yml"))
logger.info(f"Config has now following values: \n{get_value_table(Config)}")

load_translations()


bot = Client(
    intents=Intents.ALL,
    default_prefix=Config.PREFIX,
    fetch_members=True,
    debug_scope=691620697335660554,
    sync_ext=True,
    sync_interactions=True,
    delete_unused_application_cmds=True,
)


for ext in Config.EXTENSIONS:
    logger.info(f"Adding Extension {ext.name!r} ({ext.features}) from {ext.package!r}")
    bot.load_extension(".", f"{ext.package}")


event_loop.run_until_complete(db.create_tables())
bot.start(TOKEN)
