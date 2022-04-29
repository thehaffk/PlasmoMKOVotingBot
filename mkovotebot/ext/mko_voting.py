"""Cog-file for MKO voting"""
import logging

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands

from mkovotebot import settings, config
from mkovotebot.utils import MKOVotingDatabase


logger = logging.getLogger(__name__)

# TODO: /fvote <member1> <member2>
# TODO: /vote-info <member>
# TODO: /vote-top
# TODO: /funvote <member>

# TODO: Automatic hourly hours check
# TODO: Set dynamic votes ☠
# TODO: Log anything


class MKOVoting(commands.Cog):
    """
    About
    """

    def __init__(self, bot: disnake.ext.commands.Bot):
        self.bot = bot
        self.database = MKOVotingDatabase

    @commands.slash_command(
        name="vote-top",
    )
    async def vote_top(
        self,
        inter: ApplicationCommandInteraction,
    ):
        """
        Получить топ игроков по голосам

        Parameters
        ----------
        inter: ApplicationCommandInteraction object
        """

        # TODO:
        #  get roles from db via mkovotebot.utils.database.get_candidates(sort_descending=True)
        #  create top, add buttons, use view to change pages
        ...

    @commands.slash_command(
        name="vote-info",
    )
    async def vote_info(
        self,
        inter: ApplicationCommandInteraction,
        user: disnake.Member = commands.Param(lambda _: _.author),
    ):
        """
        Получить информацию об игроке

        Parameters
        ----------
        user: Игрок
        inter: ApplicationCommandInteraction object
        """
        ...

    @commands.slash_command(
        name="fvote",
        default_permission=False,
    )
    async def force_vote(
        self,
        inter: ApplicationCommandInteraction,
        voter: disnake.Member,
        candidate: disnake.Member,
    ):
        """
        Отдать голос игрока за другого игрока

        Parameters
        ----------
        voter: Избиратель
        candidate: ID Избираемый игрок
        inter: ApplicationCommandInteraction object
        """
        logger.info("%s called /fvote %s %s", inter.author.id, voter.id, candidate.id)
        # TODO: /fvote <member1> <member2>

        # Check old vote

        # Check hours

        # Write to db

        # Call update_candidate(id=candidate.id)
        ...

    @commands.slash_command(
        name="funvote",
        default_permission=False,
    )
    async def force_unvote(
        self,
        inter: ApplicationCommandInteraction,
        voter: disnake.Member,
    ):
        """
        Отдать голос игрока за другого игрока

        Parameters
        ----------
        voter: Избиратель
        candidate: ID Избираемый игрок
        inter: ApplicationCommandInteraction object
        """
        logger.info("%s called /funvote %s", inter.author.id, voter.id)
        # TODO: /funvote <member1> <member2>

        # Check old vote

        # Check hours

        # Write to db

        # Call update_candidate(id=candidate.id)
        ...

    async def cog_load(self):
        """
        Called when disnake cog is loaded
        """
        logger.info("%s Ready", __name__)


def setup(bot):
    """
    Disnake internal setup function
    """
    bot.add_cog(MKOVoting(bot))
