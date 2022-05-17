"""Cog-file for MKO voting"""
import logging

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands

from mkovotebot import settings, config
from mkovotebot.utils import MKOVotingDatabase, database, api

logger = logging.getLogger(__name__)


# TODO: /fvote <member1> <member2>
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
        self.database = MKOVotingDatabase()

    async def update_user(self, candidate_discord_id) -> bool:
        ...  # TODO
        return True

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
        #  get roles from db via mkovotebot.utils.database.get_candidates()
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

        if (
            user.guild.get_role(config.PlasmoRPGuild.player_role_id) not in user.roles
            or user.bot
        ):
            return await inter.send(
                embed=disnake.Embed(
                    color=disnake.Color.dark_red(),
                    title="❌ Ошибка",
                    description="Невозможно получить статистику у пользователя без проходки",
                ),
                ephemeral=True,
            )

        await inter.response.defer(ephemeral=True)
        await self.update_user(user.id)

        voted_user = await self.database.get_user_vote(user.id)
        if (
            voted_user is not None
            and await self.update_user(candidate_discord_id=voted_user) is True
        ):
            user_vote_string = f"Игрок проголосовал за <@{voted_user}>"
        else:
            user_vote_string = "Игрок ни за кого не проголосовал"

        voters_list = []
        for user_id in await self.database.get_candidate_votes(user.id):
            if not await self.update_user(user_id):
                continue
            voters_list.append(f"<@{user_id}>")

        voters = await self.database.get_candidate_votes(user.id)

        user_info_embed = disnake.Embed(
            color=disnake.Color.dark_green(),
            title=f"Статистика {user.display_name} "
            + (
                settings.Config.member_emoji
                if len(voters) >= settings.Config.required_mko_votes
                else ""
            ),
            description=user_vote_string,
        )
        if len(voters):
            user_info_embed.add_field(
                name=f"За {user.display_name} проголосовало: {len(voters)}",
                value=", ".join(voters_list),
                inline=False,
            )
        await inter.edit_original_message(embed=user_info_embed)

    @commands.slash_command(
        name="fvote",
    )
    @commands.default_member_permissions(manage_roles=True)
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
    )
    @commands.default_member_permissions(manage_roles=True)
    async def force_unvote(
        self,
        inter: ApplicationCommandInteraction,
        voter: disnake.Member,
    ):
        """
        Снять голос игрока

        Parameters
        ----------
        voter: Избиратель
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
