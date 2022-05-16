"""Cog-file for MKO user-voting, it`s named USER-voting because anyone can use /vote"""
import logging

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands

from mkovotebot import settings, config
from mkovotebot.utils import MKOVotingDatabase

logger = logging.getLogger(__name__)


# TODO: /vote <member>
# TODO: /unvote


class UserVoting(commands.Cog):
    """
    About
    """

    def __init__(self, bot: disnake.ext.commands.Bot):
        self.bot = bot
        self.database = MKOVotingDatabase

    @commands.has_role(config.PlasmoRPGuild.player_role_id)
    @commands.slash_command(
        name="vote",
    )
    async def user_vote(
        self, inter: ApplicationCommandInteraction, candidate: disnake.Member
    ):
        """
        Placeholder for sub commands
        """
        pass

    async def cog_load(self):
        """
        Called when disnake cog is loaded
        """
        logger.info("%s Ready", __name__)


def setup(bot):
    """
    Disnake internal setup function
    """
    bot.add_cog(UserVoting(bot))
