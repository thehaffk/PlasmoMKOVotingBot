"""Cog-file for MKO user-voting, it`s named USER-voting because anyone can use /vote"""
import logging
from datetime import datetime
from typing import Dict

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands

from mkovotebot import settings, config
from mkovotebot.utils import MKOVotingDatabase

logger = logging.getLogger(__name__)


class UserVoting(commands.Cog):
    """
    About
    """

    def __init__(self, bot: disnake.ext.commands.Bot):
        self.bot = bot
        self.database = MKOVotingDatabase()
        self.cooldowns: Dict[int, int] = {}

    @commands.default_member_permissions(manage_roles=True)
    @commands.slash_command(
        name="mko-rcd",
        guild_ids=[config.PlasmoRPGuild.id],
    )
    async def mko_rcd(self, inter: ApplicationCommandInteraction, user: disnake.Member):
        """
        Resets cooldown for user
        """
        if user.id in self.cooldowns:
            del self.cooldowns[user.id]
            await inter.response.send_message(
                f"Cooldown for {user.mention} has been reset", ephemeral=True
            )
        else:
            await inter.response.send_message(
                f"{user.mention} has no cooldown", ephemeral=True
            )

    @commands.has_role(config.PlasmoRPGuild.player_role_id)
    @commands.slash_command(name="vote", guild_ids=[config.PlasmoRPGuild.id])
    async def user_vote(
            self, inter: ApplicationCommandInteraction, candidate: disnake.Member
    ):
        """
        Проголосовать за игрока

        Parameters
        ----------
        candidate: Игрок, за которого вы хотите проголосовать
        inter: ApplicationCommandInteraction object
        """
        await inter.response.defer(ephemeral=True)
        if candidate.id == inter.author.id:
            await inter.edit_original_message("https://imgur.com/kA0qPqs")
            return

        if (
                inter.guild.get_role(config.PlasmoRPGuild.player_role_id)
                not in candidate.roles
                or candidate.bot
        ):
            await inter.edit_original_message("https://imgur.com/4hgetSA")
            return
        if self.cooldowns.get(inter.author.id, 0) > datetime.utcnow().timestamp():

            if not (await self.database.get_user_vote(inter.author.id)):
                self.cooldowns[inter.author.id] = 0
            else:
                return await inter.edit_original_message(
                    embed=disnake.Embed(
                        title="У вас кулдаун",
                        description=f"Вы сможете проголосовать только <t:{int(self.cooldowns.get(inter.author.id, 0))}:R> ",
                        color=disnake.Color.dark_red(),
                    )
                )

        old_candidate_id = await self.database.get_user_vote(voter_id=inter.author.id)
        main_mko_cog = self.bot.get_cog("MKOVoting")
        if not main_mko_cog:
            raise commands.ExtensionNotLoaded("MKOVoting")
        if old_candidate_id:
            if old_candidate_id == candidate.id:
                await inter.edit_original_message("https://imgur.com/GtS6J0X")
                return


        await self.database.set_user_vote(
            voter_id=inter.author.id, candidate_id=candidate.id
        )
        await self.bot.get_guild(config.DevServer.id).get_channel(
            config.DevServer.log_channel_id
        ).send(f"[{inter.author.id}] -> [{candidate.id}] (via /vote)")
        if await main_mko_cog.update_voter(inter.author.id):
            await inter.edit_original_message(
                embed=disnake.Embed(
                    title="Голос успешно изменен",
                    description=f"Вы проголосовали за {candidate.mention}\n\n"
                                f"Переголосовать через `/vote` можно через {settings.Config.vote_cooldown} ч.",
                    color=disnake.Color.dark_green(),
                )
            )
        else:
            await inter.edit_original_message("https://imgur.com/c2wdcbz")

        await main_mko_cog.update_candidate(candidate.id)
        if old_candidate_id:
            await main_mko_cog.update_candidate(old_candidate_id)
        self.cooldowns[inter.author.id] = datetime.utcnow().timestamp() + settings.Config.vote_cooldown * 3600

    async def cog_load(self):
        """
        Called when disnake cog is loaded
        """
        logger.info("%s Loaded  ", __name__)


def setup(bot):
    """
    Disnake internal setup function
    """
    bot.add_cog(UserVoting(bot))
