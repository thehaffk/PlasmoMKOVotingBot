import logging

import disnake
from disnake.ext import commands
from disnake.ext.commands.errors import (MissingPermissions, MissingRole,
                                         NoPrivateMessage, NotOwner)

from mkovotebot.config import PlasmoRPGuild

logger = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    """
    Handler for disnake errors
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(
        self, inter: disnake.ApplicationCommandInteraction, error
    ):
        if isinstance(error, MissingRole):
            if error.missing_role == PlasmoRPGuild.player_role_id:
                return await inter.send("https://imgur.com/PzOUMaV", ephemeral=True)
            return await inter.send(
                embed=disnake.Embed(
                    title="Ошибка",
                    description="Вам нужно "
                    f"иметь роль <@&{error.missing_role}> для использования этой команды.",
                    color=disnake.Color.red(),
                ),
                ephemeral=True,
            )
        elif isinstance(error, MissingPermissions):
            return await inter.send(
                embed=disnake.Embed(
                    title="Ошибка",
                    description="Вам нужно "
                    f"иметь пермишен **{error.missing_permissions[0]}** для использования этой команды.",
                    color=disnake.Color.red(),
                ),
                ephemeral=True,
            )
        elif isinstance(error, NotOwner):
            return await inter.send(
                embed=disnake.Embed(
                    title="Ошибка",
                    description="Вам нужно быть "
                    "администратором бота для использования этой функции\n\n"
                    "Если вам нужно использовать эту функцию,"
                    " обратитесь в тикеты Plasmo или Digital Drugs  Technologies",
                    color=disnake.Color.red(),
                ),
                ephemeral=True,
            )
        elif isinstance(error, NoPrivateMessage):
            return await inter.send(
                embed=disnake.Embed(
                    title="Команда недоступна.",
                    description="`This command cannot be used in private messages`",
                    color=disnake.Color.red(),
                ),
                ephemeral=True,
            )
        elif isinstance(error, commands.CommandOnCooldown):
            return await inter.send(
                embed=disnake.Embed(
                    title="Команда на кулдауне.",
                    description=f"Попробуйте снова через {round(error.retry_after)} секунд "
                    f"(Это {int(error.retry_after / 60 // 60)} ч. {int(error.retry_after // 60 % 60)} мин.)",
                    color=disnake.Color.red(),
                ),
                ephemeral=True,
            )
        else:
            logger.error(error)
            await inter.send(
                embed=disnake.Embed(
                    title="Ошибка",
                    description=f"Возникла неожиданная ошибка.\n\n`{error}`"
                    f"\n\nРепортить баги можно тут - https://discord.gg/JEnCvJKM",
                    color=disnake.Color.red(),
                ),
                ephemeral=True,
            )
            await self.bot.get_channel(969487104616845342).send(
                embed=disnake.Embed(
                    title="⚠⚠⚠",
                    description=f"Возникла неожиданная ошибка\n\n`{str(error)[:900]}`",
                    color=disnake.Color.brand_green(),
                ).add_field(
                    name="inter data",
                    value=f"{inter.__dict__}"[:1000],
                )
            )
            raise error

    @commands.Cog.listener()
    async def on_command_error(self, ctx: disnake.ext.commands.Context, error):
        if isinstance(error, disnake.ext.commands.errors.CommandNotFound):
            await ctx.message.add_reaction("❓")
        else:
            logger.error(error)
            await ctx.message.add_reaction("⚠")
            await ctx.send(
                embed=disnake.Embed(
                    title="Error",
                    description=f"Возникла неожиданная ошибка\n\n`{error}`"
                    f"\n\nРепортить баги можно тут - https://discord.gg/JEnCvJKM",
                    color=disnake.Color.red(),
                ),
                delete_after=10,
            )
            await self.bot.get_channel(969487104616845342).send(
                embed=disnake.Embed(
                    title="⚠⚠⚠",
                    description=f"Возникла неожиданная ошибка\n\n`{str(error)[:900]}`",
                    color=disnake.Color.brand_green(),
                ).add_field(
                    name="inter data",
                    value=f"{ctx.__dict__}"[:1000],
                )
            )
            raise error


def setup(client):
    client.add_cog(ErrorHandler(client))
