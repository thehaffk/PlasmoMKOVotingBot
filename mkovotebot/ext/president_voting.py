import logging

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands, tasks
from disnake.utils import escape_markdown

from mkovotebot import config, settings
from mkovotebot.utils import api
from mkovotebot.utils.converters import get_votes_string
from mkovotebot.utils.database import get_election_candidates
from mkovotebot.utils.models import PresidentVote

logger = logging.getLogger(__name__)


class PresidentVoteTopView(disnake.ui.View):
    def __init__(
        self,
        plasmo_guild: disnake.Guild,
    ):
        super().__init__(timeout=600)
        self.page = 1
        self.plasmo_guild = plasmo_guild

    async def generate_page(self, index: int = 1) -> disnake.Embed:
        candidates = await get_election_candidates()
        embed = disnake.Embed(
            title="Статистика выборов в президенты", color=disnake.Color.dark_green()
        )
        _from = config.maximum_candidates_per_page * (index - 1)
        _to = _from + config.maximum_candidates_per_page

        if len(candidates[_from:_to]) == 0:
            return embed.set_footer(text="На этой странице нет кандидатов")

        for place, candidate in enumerate(candidates[_from:_to]):
            place = (place + 1) + config.maximum_candidates_per_page * (index - 1)
            user = self.plasmo_guild.get_member(candidate.discord_id)
            embed.add_field(
                name=f"{place}. {user.display_name if user else '❌ not found'}",
                value=get_votes_string(candidate.votes_count),
            )
        return embed

    @disnake.ui.button(emoji="⬅️", style=disnake.ButtonStyle.secondary)
    async def prev_page(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        if not self.page == 1:
            self.page -= 1
        embed = await self.generate_page(self.page)
        await inter.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="➡️", style=disnake.ButtonStyle.secondary)
    async def next_page(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        candidates = await get_election_candidates()
        maximum_page = len(candidates) // config.maximum_candidates_per_page + int(
            bool(len(candidates) % config.maximum_candidates_per_page)
        )

        if self.page < maximum_page:
            self.page += 1
        embed = await self.generate_page(self.page)
        await inter.response.edit_message(embed=embed, view=self)


class PresidentElections(commands.Cog):
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
        current_vote = await PresidentVote.objects.filter(voter_id=discord_id).first()
        if current_vote is None:
            return False

        if (
            user is None
            or plasmo_guild.get_role(config.PlasmoRPGuild.player_role_id)
            not in user.roles
        ):
            await PresidentVote.objects.filter(voter_id=discord_id).delete()
            await self.update_candidate(current_vote.candidate_id, update_voters=False)
            return False

        played_hours = await api.get_player_hours(discord_id)
        if played_hours == -1:  # Plasmo API Error
            logger.debug("Plasmo API Error")
            return True

        if played_hours < settings.Config.president_required_weekly_hours:
            await PresidentVote.objects.filter(voter_id=discord_id).delete()
            await plasmo_guild.get_channel(
                config.PlasmoRPGuild.low_priority_announcement_channel_id
            ).send(
                content=user.mention,
                embed=disnake.Embed(
                    color=0xE02443,
                    description=f"Чтобы голосовать нужно наиграть {settings.Config.president_required_weekly_hours} ч."
                    f" за неделю \n "
                    f"У {user.mention} - {round(played_hours, 1)} ч.",
                )
                .set_author(
                    name=f"Голос {user.display_name} аннулирован",
                    icon_url="https://plasmorp.com/avatar/" + user.display_name,
                )
                .set_footer(text="Выборы президента"),
            )
            await self.update_candidate(current_vote.candidate_id, update_voters=False)
            return False

        return True

    async def update_candidate(self, discord_id: int, update_voters: bool = False):
        """
        Check candidate - hours and player role
        """
        await self.bot.wait_until_ready()

        votes = await PresidentVote.objects.filter(candidate_id=discord_id).all()

        candidate = self.bot.get_guild(config.PlasmoRPGuild.id).get_member(discord_id)
        if (
            candidate is None
            or candidate.guild.get_role(config.PlasmoRPGuild.player_role_id)
            not in candidate.roles
        ):
            await PresidentVote.objects.filter(candidate_id=discord_id).delete()
            if votes:
                logger.debug(
                    "%s is missing player role, resetting all votes", discord_id
                )
                api_profile = await api.get_user(discord_id=discord_id)
                await self.bot.get_guild(config.PlasmoRPGuild.id).get_channel(
                    config.PlasmoRPGuild.low_priority_announcement_channel_id
                ).send(
                    content=(", ".join([f"<@{vote.voter_id}>" for vote in votes])),
                    embed=disnake.Embed(
                        color=0xE02443,
                        description=f"У **"
                        f"{escape_markdown(api_profile.nick) if api_profile is not None else 'кандидата'}"
                        f"** нет роли игрока, все голоса аннулированы",
                    )
                    .set_author(
                        icon_url="https://plasmorp.com/avatar/"
                        + (
                            api_profile.nick
                            if api_profile is not None
                            else "PlasmoTools"
                        ),
                        name=f"Голоса аннулированы",
                    )
                    .set_footer(text="Выборы президента"),
                )
            return

        if update_voters:
            for vote in votes:
                await self.update_voter(discord_id=vote.voter_id)

    @commands.slash_command(name="pvote-top", dm_permission=False)
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
                color=disnake.Color.dark_green(),
            ),
            ephemeral=True,
        )

        view = PresidentVoteTopView(inter.guild)
        await inter.edit_original_message(
            embed=await view.generate_page(1),
            view=view,
        )

    @commands.slash_command(
        name="pvote-info",
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
                color=disnake.Color.dark_green(),
            ),
            ephemeral=True,
        )

        if (
            user.guild.get_role(config.PlasmoRPGuild.player_role_id) not in user.roles
            or user.bot
        ):
            await self.update_candidate(user.id)
            return await inter.edit_original_response(
                embed=disnake.Embed(
                    color=disnake.Color.dark_red(),
                    title="❌ Ошибка",
                    description="Невозможно получить статистику у пользователя без проходки",
                ),
            )

        await self.update_voter(user.id)
        await self.update_candidate(user.id)

        vote = await PresidentVote.objects.filter(voter_id=user.id).first()
        if vote is not None:
            user_vote_string = f"Игрок проголосовал за <@{vote.candidate_id}>"
        else:
            user_vote_string = "Игрок ни за кого не проголосовал"

        candidate_votes = await PresidentVote.objects.filter(candidate_id=user.id).all()
        voters_list = []
        for vote in candidate_votes:
            voter = user.guild.get_member(vote.voter_id)
            voters_list.append(escape_markdown(voter.display_name))

        user_info_embed = disnake.Embed(
            color=disnake.Color.dark_green(),
            title=f"Статистика {user.display_name}",
            description=user_vote_string,
        )
        if len(candidate_votes):
            user_info_embed.add_field(
                name=f"За {user.display_name} проголосовало: {len(candidate_votes)}",
                value=", ".join(voters_list),
                inline=False,
            )
        await inter.edit_original_message(embed=user_info_embed)

    @commands.slash_command(
        name="pfvote",
    )
    @commands.default_member_permissions(manage_guild=True)
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
        candidate: Избираемый игрок
        inter: ApplicationCommandInteraction object
        """
        logger.info("%s called /pfvote %s %s", inter.author.id, voter.id, candidate.id)
        if voter == candidate or voter.bot or candidate.bot:
            return await inter.send(
                "Правилами голосования запрещено голосовать за себя и ботов",
                ephemeral=True,
            )

        await inter.response.defer(ephemeral=True)

        await PresidentVote.objects.update_or_create(
            voter_id=voter.id, defaults={"candidate_id": candidate.id}
        )
        await self.bot.get_guild(config.DevServer.id).get_channel(
            config.DevServer.log_channel_id
        ).send(
            f"[pres] [{voter.id}] -> [{candidate.id}] ({inter.author.id}/{inter.author})\n"
            f"[{voter.display_name}] -> [{candidate.display_name}]"
        )
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

    @commands.slash_command(
        name="pfunvote",
    )
    @commands.default_member_permissions(manage_guild=True)
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
        logger.info("%s called /pfunvote %s", inter.author.id, voter.id)
        await inter.response.defer(ephemeral=True)

        old_vote = await PresidentVote.objects.filter(voter_id=voter.id).first()
        if old_vote:
            await PresidentVote.objects.filter(voter_id=voter.id).delete()
            await self.update_candidate(old_vote.candidate_id)

        await self.bot.get_guild(config.DevServer.id).get_channel(
            config.DevServer.log_channel_id
        ).send(
            f"[pres] [{voter.id}] -> [CLEARED] ({inter.author.id}/{inter.author})\n"
            f"[{voter.display_name}] -> [CLEARED]"
        )
        await inter.edit_original_message(
            embed=disnake.Embed(
                title="Голос успешно изменен",
                description=f"Голос {voter.mention} сброшен",
                color=disnake.Color.dark_green(),
            )
        )
        return True

    @commands.is_owner()
    @commands.default_member_permissions(manage_roles=True)
    @commands.slash_command(
        name="reset-president-voting",
        guild_ids=[config.PlasmoRPGuild.id, config.TestServer.id],
    )
    async def reset_president_voting_command(
        self, inter: ApplicationCommandInteraction
    ):
        await inter.response.defer(ephemeral=True)
        await PresidentVote.objects.delete()

        await inter.edit_original_message("👍 Дело сделано")

    async def update_all_users(self):
        candidates = set(
            [vote.candidate_id for vote in await PresidentVote.objects.all()]
        )
        for candidate_id in candidates:
            await self.update_candidate(candidate_id, update_voters=True)

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
    bot.add_cog(PresidentElections(bot))
