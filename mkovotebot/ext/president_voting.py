"""
Cog-file for MKO voting
"""
import logging

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands

from mkovotebot import settings, config
from mkovotebot.utils import PresidentElectionsDatabase


logger = logging.getLogger(__name__)


# TODO: /pvote-info <member>
# TODO: /pvote-top
# TODO: /pfvote <member1> <member2>
# TODO: /pfunvote <member>

# TODO: Automatic hours-check
# TODO: Get user hours function
# TODO: Set dynamic votes
# TODO: Logger


class Main(commands.Cog):
    """
    About
    """

    def __init__(self, bot: disnake.ext.commands.Bot):
        self.bot = bot
        self.database = PresidentElectionsDatabase()

    @commands.slash_command(
        name="pfvote",
    )
    async def force_vote(
        self,
        inter: ApplicationCommandInteraction,
        voter: disnake.Member,
        candidate: disnake.Member,
    ):
        """
        4
        """
        pass

    # TODO: /pvote-info
    # TODO: /pvote-top <member>
    # TODO: /pvunvote <member>
    # TODO: Automatic hourly

    async def cog_load(self):
        """
        Called when disnake cog is loaded
        """
        logger.info("%s Ready", __name__)


def setup(bot):
    """
    Disnake internal setup function
    """
    bot.add_cog(Main(bot))
