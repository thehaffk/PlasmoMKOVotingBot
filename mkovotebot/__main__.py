import logging

import asyncio

from mkovotebot import settings, config, log
from mkovotebot.bot import MKOVoteBot
from mkovotebot.utils.database import PresidentElectionsDatabase, MKOVotingDatabase

log.setup()

bot = MKOVoteBot.create()
logger = logging.getLogger(__name__)

bot.load_extension("mkovotebot.ext.error_handler")

if settings.Config.mko_voting_enabled:
    logger.info("Loading mkovotebot.ext.mko_voting")
    bot.load_extension("mkovotebot.ext.mko_voting")

    database = MKOVotingDatabase()
    asyncio.run(database.setup())
    del database

    if settings.Config.user_voting_enabled:
        logger.debug("Loading mkovotebot.ext.mko_user_voting")
        bot.load_extension("mkovotebot.ext.mko_user_voting")

if settings.Config.president_voting_enabled:
    logger.debug("Loading mkovotebot.ext.president_voting")
    bot.load_extension("mkovotebot.ext.president_voting")
    # if settings.Config.president_user_voting_enabled:
    #     bot.load_extension("mkovotebot.ext.president_user_voting")

    database = PresidentElectionsDatabase()
    asyncio.run(database.setup())
    del database

bot.run(config.TOKEN)
