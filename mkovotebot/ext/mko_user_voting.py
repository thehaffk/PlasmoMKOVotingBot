import logging
from datetime import datetime

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands

from mkovotebot import config, settings
from mkovotebot.ext.mko_voting import MKOVoting
from mkovotebot.utils import models

logger = logging.getLogger(__name__)


class UserVoting(commands.Cog):
    def __init__(self, bot: disnake.ext.commands.Bot):
        self.bot = bot

    @commands.default_member_permissions(manage_roles=True)
    @commands.slash_command(
        name="mko-rcd", guild_ids=[config.PlasmoRPGuild.id, config.TestServer.id]
    )
    async def mko_rcd(self, inter: ApplicationCommandInteraction, user: disnake.Member):
        """
        Resets cooldown for user
        """
        await models.Cooldown.objects.update_or_create(
            voter_id=user.id, defaults={"mko_cooldown": 0}
        )
        await inter.response.send_message(
            f"Cooldown for {user.mention} has been reset", ephemeral=True
        )

    @commands.has_role(config.PlasmoRPGuild.player_role_id)
    @commands.slash_command(name="vote")
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
            return await inter.edit_original_message("https://imgur.com/kA0qPqs")

        if (
            inter.guild.get_role(config.PlasmoRPGuild.player_role_id)
            not in candidate.roles
            or candidate.bot
        ):
            return await inter.edit_original_message("https://imgur.com/4hgetSA")

        cooldown, _ = await models.Cooldown.objects.get_or_create(
            voter_id=inter.author.id, defaults={"mko_cooldown": 0}
        )
        if cooldown.mko_cooldown > datetime.utcnow().timestamp():
            return await inter.edit_original_message(
                embed=disnake.Embed(
                    title="Команда на кулдауне",
                    description=f"Вы сможете проголосовать <t:{cooldown.mko_cooldown}:R> ",
                    color=disnake.Color.dark_red(),
                )
            )

        old_vote = await models.MKOVote.objects.filter(voter_id=inter.author.id).first()
        main_mko_cog: MKOVoting = self.bot.get_cog("MKOVoting")
        if not main_mko_cog:
            raise commands.ExtensionNotLoaded("MKOVoting")

        if old_vote is not None and old_vote.candidate_id == candidate.id:
            return await inter.edit_original_message("https://imgur.com/GtS6J0X")

        await models.MKOVote.objects.update_or_create(
            voter_id=inter.author.id, defaults={"candidate_id": candidate.id}
        )
        await self.bot.get_guild(config.DevServer.id).get_channel(
            config.DevServer.log_channel_id
        ).send(
            f"[mko] [{inter.author.id}] -> [{candidate.id}] (via /vote)\n"
            f"[{inter.author.display_name}] -> [{candidate.display_name}]"
        )
        if old_vote:
            await main_mko_cog.update_candidate(old_vote.candidate_id)

        if not await main_mko_cog.update_voter(inter.author.id):
            return await inter.edit_original_message("https://imgur.com/c2wdcbz")
        await inter.edit_original_message(
            embed=disnake.Embed(
                title="Голос успешно изменен",
                description=f"Вы проголосовали за {candidate.mention}\n\n"
                f"Переголосовать через `/vote` можно "
                f"<t:{int(datetime.utcnow().timestamp() + settings.Config.vote_cooldown * 3600)}:R> ",
                color=disnake.Color.dark_green(),
            )
        )

        await main_mko_cog.update_candidate(candidate.id)
        await models.Cooldown.objects.update_or_create(
            voter_id=inter.author.id,
            defaults={
                "mko_cooldown": int(
                    datetime.utcnow().timestamp() + settings.Config.vote_cooldown * 3600
                ),
            },
        )

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
