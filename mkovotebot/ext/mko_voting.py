import logging

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands, tasks
from disnake.utils import escape_markdown

from mkovotebot import settings, config
from mkovotebot.utils import api, models
from mkovotebot.utils.converters import get_votes_string
from mkovotebot.utils.database import get_mko_candidates

logger = logging.getLogger(__name__)

class MKOVoteTopView(disnake.ui.View):
    def __init__(
        self,
        plasmo_guild: disnake.Guild,
    ):
        super().__init__(timeout=600)
        self.page = 1
        self.plasmo_guild = plasmo_guild

    async def generate_page(self, index: int = 1) -> disnake.Embed:
        candidates = await get_mko_candidates()
        embed = disnake.Embed(
            title="Топ игроков по голосам", color=disnake.Color.dark_green()
        ).set_footer(
            text=f"Страница {self.page} | Чтобы попасть в совет нужно "
                 f"{get_votes_string(settings.Config.required_mko_votes)}")
        _from = config.maximum_candidates_per_page * (index - 1)
        _to = _from + config.maximum_candidates_per_page

        if not candidates[_from:_to]:
            embed.description = "На этой странице нет кандидатов"
            return embed


        for place, candidate in enumerate(candidates[_from:_to]):
            place = (place + 1) + config.maximum_candidates_per_page * (index - 1)
            user = self.plasmo_guild.get_member(candidate.discord_id)
            embed.add_field(
                name=f"{place}. {user.display_name if user else 'not found'}"
                + (
                    settings.Config.member_emoji
                    if candidate.votes_count >= settings.Config.required_mko_votes
                    and isinstance(user, disnake.Member)
                    else ""
                ),
                value=get_votes_string(candidate.votes_count),
            )
        return embed

    @disnake.ui.button(emoji="⬅️", style=disnake.ButtonStyle.secondary)
    async def prev_page(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        # todo: use 🔄 when page == 1
        if not self.page == 1:
            self.page -= 1
        embed = await self.generate_page(self.page)
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="➡️", style=disnake.ButtonStyle.secondary)
    async def next_page(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        candidates = await get_mko_candidates()
        maximum_page = len(candidates) // config.maximum_candidates_per_page + int(
            bool(len(candidates) % config.maximum_candidates_per_page)
        )

        if self.page < maximum_page:
            self.page += 1
        embed = await self.generate_page(self.page)
        await inter.response.edit_message(embed=embed, view=self)


class MKOVoting(commands.Cog):
    def __init__(self, bot: disnake.ext.commands.Bot):
        self.bot = bot

    async def update_voter(self, discord_id: int) -> bool:
        """
        Check voter - hours and player role

        :return - True if vote is active
        """
        await self.bot.wait_until_ready()
        plasmo_guild = self.bot.get_guild(config.PlasmoRPGuild.id)
        user = plasmo_guild.get_member(discord_id)
        current_vote = await models.MKOVote.objects.filter(voter_id=discord_id).first()
        if current_vote is None:
            return False

        if (
            user is None
            or plasmo_guild.get_role(config.PlasmoRPGuild.player_role_id)
            not in user.roles
        ):
            await models.MKOVote.objects.filter(voter_id=discord_id).delete()
            await self.update_candidate(current_vote.candidate_id, update_voters=False)
            return False

        played_hours = await api.get_player_hours(discord_id)
        if played_hours == -1:  # Plasmo API Error
            logger.debug("Plasmo API Error")
            return True

        if played_hours < settings.Config.mko_required_weekly_hours:
            await models.MKOVote.objects.filter(voter_id=discord_id).delete()
            await plasmo_guild.get_channel(
                config.PlasmoRPGuild.low_priority_announcement_channel_id
            ).send(
                content=user.mention,
                embed=disnake.Embed(
                    color=0xE02443,
                    description=f"Чтобы голосовать нужно наиграть {settings.Config.mko_required_weekly_hours} ч."
                                f" за неделю \n "
                    f"У {user.mention} - {round(played_hours, 1)} ч.",
                ).set_author(name=f"Голос {escape_markdown(user.display_name)} аннулирован",
                             icon_url="https://plasmorp.com/avatar/" + user.display_name).set_footer(
                    text="Голосование МКО"
                ),
            )
            await self.update_candidate(current_vote.candidate_id, update_voters=False)
            return False

        return True

    async def update_candidate(self, discord_id: int, update_voters: bool = False) -> bool:
        """
        Check candidate - hours and player role

        :return - True if candidate is parliament member
        """
        await self.bot.wait_until_ready()

        votes = await models.MKOVote.objects.filter(candidate_id=discord_id).all()

        candidate = self.bot.get_guild(config.PlasmoRPGuild.id).get_member(discord_id)
        if (
            candidate is None
            or candidate.guild.get_role(config.PlasmoRPGuild.player_role_id)
            not in candidate.roles
        ):
            await models.MKOVote.objects.filter(candidate_id=discord_id).delete()
            if votes:
                api_profile = await api.get_user(discord_id=discord_id)
                await self.bot.get_guild(config.PlasmoRPGuild.id).get_channel(
                    config.PlasmoRPGuild.announcement_channel_id
                    if len(votes) >= settings.Config.required_mko_votes
                    else config.PlasmoRPGuild.low_priority_announcement_channel_id
                ).send(
                    content=(", ".join([f"<@{vote.voter_id}>" for vote in votes])),
                    embed=disnake.Embed(
                        color=0xE02443,
                        description=f"У **"
                                    f"{escape_markdown(api_profile.nick) if api_profile is not None else 'кандидата'}"
                                    f"** нет роли игрока, все голоса аннулированы",
                    ).set_author(
                        icon_url="https://plasmorp.com/avatar/"
                        + (api_profile.nick if api_profile is not None else "PlasmoTools"),
                        name=f"Голоса аннулированы"
                    ).set_footer(
                    text="Голосование МКО"
                ),
                )
                logger.debug("%s is missing player role, resetting all votes", discord_id)
            return False

        if update_voters:
            for vote in votes:
                await self.update_voter(discord_id=vote.voter_id)
            votes = await models.MKOVote.objects.filter(candidate_id=discord_id).all()

        mko_member_role = candidate.guild.get_role(config.PlasmoRPGuild.mko_member_role_id)
        if len(votes) >= settings.Config.required_mko_votes:
            if mko_member_role not in candidate.roles:
                await candidate.add_roles(mko_member_role, reason="New MKO member")
                await candidate.guild.get_channel(
                    config.PlasmoRPGuild.announcement_channel_id
                ).send(
                    content=candidate.mention,
                    embed=disnake.Embed(
                        color=0x17BF63,
                        title="📃 Новый участник совета",
                        description=candidate.mention + f" набрал {get_votes_string(votes_count=len(votes))} "
                                                        f"и прошел в совет",
                    ).set_thumbnail(
                        url="https://plasmorp.com/avatar/" + candidate.display_name
                    ),
                )
            try:
                mko_guild = self.bot.get_guild(config.MKOStructureGuild.id)
                if mko_guild:
                    if not candidate.id in [_.id for _ in mko_guild.members]:
                        logger.info("Sending invite to %s", candidate.display_name)
                        await candidate.send(
                            content=config.MKOStructureGuild.invite_url,
                            embed=disnake.Embed(
                                title="Вы прошли в совет МКО, советуем зайти в дискорд структуры, чтобы быть в "
                                      "курсе всех новостей и анонсов",
                                color=disnake.Color.dark_green()
                            )
                        )
            except disnake.Forbidden:
                pass
            return True
        else:
            if mko_member_role in candidate.roles:
                await candidate.remove_roles(
                    mko_member_role, reason="Not enough votes to be MKO member"
                )
                await candidate.guild.get_channel(
                    config.PlasmoRPGuild.announcement_channel_id
                ).send(
                    content=candidate.mention,
                    embed=disnake.Embed(
                        color=0xE02443,
                        title="❌ Игрок покидает совет",
                        description=candidate.mention
                        + " потерял голоса, нужные для участия в совете",
                    ).set_thumbnail(
                        url="https://rp.plo.su/avatar/" + candidate.display_name
                    ),
                )
            return False


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

        await inter.send(
            embed=disnake.Embed(
                description="<a:loading2:995519203140456528> Подождите, генерирую страницу",
                color=disnake.Color.dark_green()
            ),
            ephemeral=True
        )

        view = MKOVoteTopView(plasmo_guild=inter.guild)
        await inter.edit_original_message(
            embed=await view.generate_page(1),
            view=view,
        )

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

        await inter.send(
            embed=disnake.Embed(
                description="<a:loading2:995519203140456528> Подождите, обновляю информацию и генерирую профиль",
                color=disnake.Color.dark_green()
            ),
            ephemeral=True
        )
        await self.update_voter(user.id)
        await self.update_candidate(user.id, update_voters=True)

        if (
            user.guild.get_role(config.PlasmoRPGuild.player_role_id) not in user.roles
            or user.bot
        ):
            await self.update_candidate(user.id)
            return await inter.edit_original_message(
                embed=disnake.Embed(
                    color=disnake.Color.dark_red(),
                    title="❌ Ошибка",
                    description="Невозможно получить статистику у пользователя без проходки",
                ),
            )

        user_vote = await models.MKOVote.objects.filter(voter_id=user.id).first()
        if user_vote is not None:
            user_vote_string = f"Игрок проголосовал за <@{user_vote.candidate_id}>"
        else:
            user_vote_string = "Игрок не голосовал"

        candidate_votes = await models.MKOVote.objects.filter(candidate_id=user.id).all()
        voters_list = []
        for vote in candidate_votes:
            voter = user.guild.get_member(vote.voter_id)
            voters_list.append(escape_markdown(voter.display_name))

        user_info_embed = disnake.Embed(
            color=disnake.Color.dark_green(),
            title=f"Статистика {user.display_name}"
            + (
              (" " + settings.Config.member_emoji)
                if len(candidate_votes) >= settings.Config.required_mko_votes
                else ""
            ),
            description=user_vote_string,
        )
        if len(candidate_votes):
            user_info_embed.add_field(
                name=f"За {escape_markdown(user.display_name)} проголосовало: {len(candidate_votes)}",
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
        if voter == candidate or voter.bot or candidate.bot:
            return await inter.send(
                "Правилами голосования нельзя голосовать за самого себя и ботов",
                ephemeral=True,
            )

        await inter.response.defer(ephemeral=True)
        old_vote = await models.MKOVote.objects.filter(voter_id=voter.id).first()

        await models.MKOVote.objects.update_or_create(
            voter_id=voter.id,
            defaults={
                "candidate_id": candidate.id
            }
        )


        await self.bot.get_guild(config.DevServer.id).get_channel(
            config.DevServer.log_channel_id
        ).send(f"[mko] [{voter.id}] -> [{candidate.id}] ({inter.author.id}/{inter.author})\n"
               f"[{voter.display_name}] -> [{candidate.display_name}]")
        if await self.update_voter(voter.id):
            await inter.edit_original_message(
                embed=disnake.Embed(
                    title="Голос успешно изменен",
                    description=f"Голос {voter.mention} отдан за {candidate.mention}",
                    color=disnake.Color.dark_green(),
                )
            )
        else:
            await inter.edit_original_message(
                embed=disnake.Embed(
                    title="Голос обработан",
                    description=f"Голос обработан, но сразу же аннулирован",
                    color=disnake.Color.yellow(),
                )
            )

        await self.update_candidate(candidate.id)
        if old_vote is not None:
            await self.update_candidate(old_vote.candidate_id)

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
        await inter.response.defer(ephemeral=True)

        old_vote = await models.MKOVote.objects.filter(voter_id=voter.id).first()
        if old_vote is not None:
            await models.MKOVote.objects.filter(voter_id=voter.id).delete()
            await self.update_candidate(old_vote.candidate_id)

        if old_vote:
            await self.bot.get_guild(config.DevServer.id).get_channel(
                config.DevServer.log_channel_id
            ).send(f"[mko] [{voter.id}] -> [CLEARED] ({inter.author.id}/{inter.author})\n"
                   f"[{voter.display_name}] -> [CLEARED]")
        await inter.edit_original_message(
            embed=disnake.Embed(
                title="Голос успешно изменен",
                description=f"Голос {voter.mention} сброшен",
                color=disnake.Color.dark_green(),
            )
        )
        return True

    async def update_all_users(self):
        plasmo_guild = self.bot.get_guild(config.PlasmoRPGuild.id)
        mko_member_role_owners = [
            user.id
            for user in plasmo_guild.get_role(
                config.PlasmoRPGuild.mko_member_role_id
            ).members
        ]
        candidates = [
            candidate.discord_id for candidate in await get_mko_candidates()
        ]
        for candidate in set(mko_member_role_owners + candidates):
            await self.update_candidate(candidate, update_voters=True)

    @tasks.loop(hours=8)
    async def update_all_users_task(self):
        await self.update_all_users()

    @update_all_users_task.before_loop
    async def before_task(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_ready")
    async def on_ready_listener(self):
        if not self.update_all_users_task.is_running():
            self.update_all_users_task.start()

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
