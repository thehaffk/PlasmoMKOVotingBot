import logging

from mkovotebot import settings, config, log
from mkovotebot.bot import MKOVoteBot

log.setup()

bot = MKOVoteBot.create()
logger = logging.getLogger(__name__)

if settings.Config.mko_voting_enabled:
    logger.info("Loading mkovotebot.ext.mko_voting")
    bot.load_extension("mkovotebot.ext.mko_voting")

if settings.Config.user_voting_enabled:
    logger.debug("Loading mkovotebot.ext.mko_user_voting")
    bot.load_extension("mkovotebot.ext.mko_user_voting")

if settings.Config.president_voting_enabled:
    logger.debug("Loading mkovotebot.ext.president_voting")
    bot.load_extension("mkovotebot.ext.president_voting")

bot.run(config.TOKEN)  # 1
