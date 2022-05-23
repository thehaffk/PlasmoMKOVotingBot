"""Cog-file for MKO voting"""
import logging

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands, tasks

from mkovotebot import settings, config
from mkovotebot.utils import PresidentElectionsDatabase, api, get_votes_string

logger = logging.getLogger(__name__)


# TODO: This is terrible, just a copy of mko_voting.py, i don`t know what to do with it...


class PresidentVoteTopView(disnake.ui.View):
    def __init__(
        self,
        plasmo_guild: disnake.Guild,
    ):
        super().__init__(timeout=600)
        self.page = 1
        self.plasmo_guild = plasmo_guild
        self.database = PresidentElectionsDatabase()

    async def generate_page(self, index: int = 1) -> disnake.Embed:
        candidates = await self.database.get_candidates()
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
                name=f"{place}. {user.display_name if user else '❌ DELETED'}",
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
        candidates = await self.database.get_candidates()
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
        self.database = PresidentElectionsDatabase()

    async def update_voter(self, discord_id, avoid_circular_calls=False) -> bool:
        """
        Check voter - hours and player role

        :return - True if voter`s vote is active
        """
        plasmo_guild = self.bot.get_guild(config.PlasmoRPGuild.id)
        user = plasmo_guild.get_member(discord_id)
        candidate_id = await self.database.get_user_vote(discord_id)
        if candidate_id is None:
            return False

        if (
            user is None
            or plasmo_guild.get_role(config.PlasmoRPGuild.player_role_id)
            not in user.roles
        ):
            await self.database.set_user_vote(voter_id=discord_id, candidate_id=None)
            if not avoid_circular_calls:
                await self.update_candidate(candidate_id)
            return False

        played_hours = await api.get_player_hours(discord_id)
        if played_hours == -1:  # Plasmo API Error
            return True

        if played_hours < settings.Config.required_weekly_hours:
            await self.database.set_user_vote(voter_id=discord_id, candidate_id=None)
            await plasmo_guild.get_channel(
                config.PlasmoRPGuild.low_priority_announcement_channel_id
            ).send(
                content=user.mention,
                embed=disnake.Embed(
                    color=disnake.Color.dark_red(),
                    title="❌ Ваш голос аннулирован",
                    description=f"Чтобы голосовать на выборах на выборах нужно наиграть "
                    f"хотя бы {settings.Config.required_weekly_hours} ч. за неделю \n "
                    f"||У вас - {round(played_hours, 2)} ч.||",
                ).set_thumbnail(url="https://rp.plo.su/avatar/" + user.display_name),
            )
            await self.update_candidate(candidate_id)
            return False

        return True

    async def update_candidate(self, discord_id) -> bool:
        """
        Check candidate - hours and player role
        """
        votes = await self.database.get_candidate_votes(discord_id)
        user = self.bot.get_guild(config.PlasmoRPGuild.id).get_member(discord_id)
        if user is None or config.PlasmoRPGuild.player_role_id not in [
            role.id for role in user.roles
        ]:
            await self.update_voter(discord_id, avoid_circular_calls=True)
            if len(votes) > 0:
                plasmo_user = await api.get_user(discord_id=discord_id)
                await self.bot.get_guild(config.PlasmoRPGuild.id).get_channel(
                    config.PlasmoRPGuild.announcement_channel_id
                ).send(
                    content=(", ".join([f"<@{user_id}>" for user_id in votes])),
                    embed=disnake.Embed(
                        color=disnake.Color.dark_red(),
                        title="❌ Голоса аннулированны",
                        description=f"У **{plasmo_user.nick if plasmo_user is not None else 'кандидата в президенты'}** "
                        f"нет роли игрока на Plasmo RP, все голоса аннулированы",
                    ).set_thumbnail(
                        url="https://rp.plo.su/avatar/"
                        + (plasmo_user.nick if plasmo_user is not None else "___")
                    ),
                )
            logger.debug("Unable to get %s, resetting all votes", discord_id)
            await self.database.reset_candidate_votes(discord_id)
            return False

    @commands.slash_command(
        name="pvote-top",
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

        await inter.response.defer(ephemeral=True)

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

        if (
            user.guild.get_role(config.PlasmoRPGuild.player_role_id) not in user.roles
            or user.bot
        ):
            await self.update_candidate(user.id)
            return await inter.send(
                embed=disnake.Embed(
                    color=disnake.Color.dark_red(),
                    title="❌ Ошибка",
                    description="Невозможно получить статистику у пользователя без проходки",
                ),
                ephemeral=True,
            )

        await inter.response.defer(ephemeral=True)

        await self.update_voter(user.id)
        await self.update_candidate(user.id)

        voted_user = await self.database.get_user_vote(user.id)
        if voted_user is not None:
            user_vote_string = f"Игрок проголосовал за <@{voted_user}>"
        else:
            user_vote_string = "Игрок ни за кого не проголосовал"

        voters_list = []
        for user_id in await self.database.get_candidate_votes(user.id):
            if not await self.update_voter(user_id):
                continue
            voters_list.append(f"<@{user_id}>")

        voters = await self.database.get_candidate_votes(user.id)

        user_info_embed = disnake.Embed(
            color=disnake.Color.dark_green(),
            title=f"Статистика {user.display_name}",
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
        candidate: ID Избираемый игрок
        inter: ApplicationCommandInteraction object
        """
        logger.info("%s called /pfvote %s %s", inter.author.id, voter.id, candidate.id)
        if voter == candidate or voter.bot or candidate.bot:
            return await inter.send(
                "Я тебе просто объясню как будет, я знаю, уже откуда ты, и вижу как ты подключен, "
                "я сейчас беру эту инфу и просто не поленюсь и пойду в полицию, и хоть у тебя и "
                "динамический iр , но Бай-флай хранит инфо 3 года, о запросах абонентов и их подключении, "
                "так что узнать у кого был IР в ото время дело пары минут, а дальше статья за разжигание "
                "межнациональной розни и о нормальной работе или учёбе да и о жизни, можешь забыть, "
                "мой тебе совет",
                ephemeral=True,
            )

        await inter.response.defer(ephemeral=True)

        await self.database.set_user_vote(voter_id=voter.id, candidate_id=candidate.id)
        await self.bot.get_guild(config.DevServer.id).get_channel(
            config.DevServer.log_channel_id
        ).send(f"[{voter.id}] -> [{candidate.id}] ({inter.author.id}/{inter.author})")
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

        old_vote = await self.database.get_user_vote(voter_id=voter.id)
        if old_vote:
            await self.database.set_user_vote(voter_id=voter.id, candidate_id=None)
            await self.update_candidate(old_vote)

        await self.bot.get_guild(config.DevServer.id).get_channel(
            config.DevServer.log_channel_id
        ).send(f"[{voter.id}] -> [CLEARED] ({inter.author.id}/{inter.author})")
        await inter.edit_original_message(
            embed=disnake.Embed(
                title="Голос успешно изменен",
                description=f"Голос {voter.mention} сброшен",
                color=disnake.Color.dark_green(),
            )
        )
        return True

    @tasks.loop(hours=8)
    async def update_all_users(self):
        candidates = [
            candidate.discord_id for candidate in await self.database.get_candidates()
        ]
        for candidate in candidates:
            for voter in await self.database.get_candidate_votes(candidate):
                await self.update_voter(voter)
            await self.update_candidate(candidate)

    @update_all_users.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_ready")
    async def on_ready_listener(self):
        await self.update_all_users()

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
