from lib.db import db
import discord
from discord import utils
from discord.ext import commands
from settings import config, texts, errors
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import time

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)
bot.remove_command('help')


def autoUpdater(sched):
    sched.add_job(update_members, CronTrigger(hour=12))
    #sched.add_job(update_tops, CronTrigger(minute=30))


# запрос к бд - получение количества часов за неделю
def get_played_hours(discord_id, in_seconds=False):
    uuid = db.select(table="users", columns="uuid", where=f"discord_id = {discord_id}")[0]
    if uuid is None:
        return 0
    uuid = (uuid[0:8] + '-' + uuid[8:12] + '-' + uuid[12:16] + '-' + uuid[16:20] + '-' + uuid[20:])
    seconds = db.select(table='stats_month', columns='SUM(played)', where=f'uuid = "{uuid}" AND date >= (CURDATE()-7)')[
        0]
    if not seconds:
        return 0
    if in_seconds:
        return seconds
    else:
        return seconds / 60 // 60


# запрос к бд - получение количества пользователей
def get_votes(discord_id, return_users=False):
    res = db.select(columns='COUNT(*) as votes', where=f'voted_user = {discord_id}',
                    args='GROUP BY voted_user')
    if not return_users:
        return 0 if res is None else res[0]
    elif res is None:
        return []
    else:
        arr = db.select(columns='discord_id', where=f'voted_user = {discord_id}')
        responce = []
        if len(arr) != 1:
            for elem in arr:
                responce.append(elem[0])
        else:
            responce = [arr[0]]
        return responce


# рофлан получение мембера по howkawgew или <@91301293123>
def get_player_by_str(ctx, player):
    try:
        if '<@' in player and '>' in player:
            print(int(player[(3 if '!' in player else 2):-1]))
            return ctx.guild.get_member(int(player[(3 if '!' in player else 2):-1]))
        else:
            member = utils.get(ctx.guild.members, nick=player)
            if not member:
                member = utils.get(ctx.guild.members, name=player)
            if member:
                member = member.id
            else:
                raise Exception
            user = ctx.guild.get_member(member)
            return user

    except Exception as e:
        print(e)
        return None


# проверка на канал
def channel_check(ctx):
    if ctx.channel.id in config['trusted'] and config['channel_filtering']:
        return True
    elif not config['channel_filtering']:
        return True
    else:
        return False


# Логгер Kappa, логирует почти все успешные выводы комманд
async def logger(ctx=None, type=None, player1=None, player2=None):
    if type == 'voted':
        embed = discord.Embed(title=texts['voted_title'],
                              description=texts['voted_desk'].format(player1=player1.mention, player2=player2.mention),
                              colour=texts['voted_color'])
        embed.set_thumbnail(url=f'https://rp.plo.su/avatar/{player2.display_name}')
        await ctx.send(embed=embed)
    elif type == 'fvoted':
        embed = discord.Embed(title=texts['fvoted_title'],
                              description=texts['fvoted_desk'].format(player1=player1.mention, player2=player2.mention),
                              colour=texts['fvoted_color'])
        embed.set_thumbnail(url=f'https://rp.plo.su/avatar/{player2.display_name}')
        await ctx.send(embed=embed)
    elif type == 'unvoted':
        embed = discord.Embed(title=texts['unvoted_title'],
                              description=texts['unvoted_desk'].format(player1=player1.mention),
                              colour=texts['unvoted_color'])
        embed.set_thumbnail(url=f'https://rp.plo.su/avatar/{player1.display_name}')
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif type == 'added_parlmanent_member':
        embed = discord.Embed(title=texts['added_pmember_title'],
                              description=texts['added_pmember_desk'].format(player1=player1.mention),
                              colour=texts['added_pmember_color'])
        embed.set_thumbnail(url=f'https://rp.plo.su/avatar/{player1.display_name}')
        await pLogs.send(f'{player1.mention}', embed=embed)
    elif type == 'removed_parlmanent_member':
        embed = discord.Embed(title=texts['removed_pmember_title'],
                              description=texts['removed_pmember_desk'].format(player1=player1.mention),
                              colour=texts['removed_pmember_color'])
        embed.set_thumbnail(url=f'https://rp.plo.su/avatar/{player1.display_name}')
        await pLogs.send(f'{player1.mention}', embed=embed)
    elif type == 'rejected_vote':
        embed = discord.Embed(title=texts['rejected_vote_title'],
                              description=texts['rejected_vote_desk'].format(hours=config['hours_to_vote']),
                              colour=texts['rejected_vote_color'])
        embed.set_thumbnail(url=f'https://rp.plo.su/avatar/{player1.display_name}')
        await aLogs.send(f'{player1.mention}', embed=embed)
    elif type == 'rcd':
        embed = discord.Embed(title=texts['rcd_title'],
                              description=texts['rcd_desk'].format(player=player1.mention),
                              colour=texts['rcd_color'])
        embed.set_thumbnail(url=f'https://rp.plo.su/avatar/{player1.display_name}')
        await ctx.send(f'{player1.mention}', embed=embed)


# Возвращает двумерный массив в формате [кол-во голосов, айди]
def top():
    voted_users = db.select(columns='DISTINCT voted_user', return_list=True)
    users = []
    for user in voted_users:
        users.append([get_votes(user), int(user)])
    if len(users) == 0:
        return users
    users.sort(key=lambda x: x[0], reverse=True)
    return users


# не работает. обновляет все топи
async def update_tops():
    print('pepega tops')


# обновление членства в совете
async def update_member(member):
    votes_check = True if get_votes(member.id) >= config['votes_to_member'] else False
    is_member = True if member_role in Pguild.get_member(member.id).roles else False
    if votes_check and is_member:
        return True
    elif votes_check and not is_member:
        await logger(type='added_parlmanent_member', player1=member)
        await Pguild.get_member(member.id).add_roles(member_role)
    elif not votes_check and is_member:
        await logger(type='removed_parlmanent_member', player1=member)
        await Pguild.get_member(member.id).remove_roles(member_role)


# обновление членства в совете у всех игроков
async def update_members():
    users = db.select(columns='DISTINCT voted_user', return_list=True)
    for user in users:
        await update_member(Pguild.get_member(int(user)))


@bot.command()
@commands.has_role(config['player'])
async def vote(ctx, player):
    if not channel_check(ctx):
        return 'Pepega'

    player = get_player_by_str(ctx, player)
    if player is None:
        await vote_error(ctx, error='BadArgument')
        return None

    if player_role not in player.roles:
        await vote_error(ctx, error='PlayerMissingRole', player=player)
        return None

    if player == ctx.author:
        await vote_error(ctx, error='SelfVoting')
        return None

    if get_played_hours(ctx.author.id) < config['hours_to_vote']:
        await vote_error(ctx, error='TooFewHours')
        return None

    # START of copy-paste code
    AV = False  # Предполагается изменение голоса, а не добавление нового
    vote = db.select(columns='voted_user, last_vote_timestamp', where=f'discord_id = {ctx.author.id}')
    if vote is not None:
        if vote[1] + config['vote_cooldown'] > time.time():
            await vote_error(ctx, 'Cooldown')
            return False
        if int(vote[0]) == player.id:
            await vote_error(ctx, 'AlreadyVoted', player=player)
            return False
        db.update(data=f'voted_user = {player.id}, last_vote_timestamp={int(time.time())}',
                  where=f'discord_id={ctx.author.id}')
        AV = True
    # END of copy-paste code
    else:
        db.insert(
            data=f'id=NULL, discord_id={ctx.author.id},voted_user={player.id}, last_vote_timestamp={int(time.time())}')

    if AV:
        await update_member(Pguild.get_member(int(vote[0])))
    await update_member(player)
    await logger(ctx, type='voted', player1=ctx.author, player2=player)


# Меняет presence
@bot.command()
async def activity(ctx, *, text):
    if ctx.author.id == 737501414141591594:
        await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(str(text)))


# П OMEGALUL Х У Й
@activity.error
async def pokhuy(ctx, error):
    pass  # eq. to похуй


@vote.error
async def vote_error(ctx, error, player=None):
    if not channel_check(ctx):
        return 'Pepega'
    if isinstance(error, commands.errors.MissingRole):
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Vote MissingRole'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Vote MissingRequiredArgument'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif error == 'PlayerMissingRole':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Vote PlayerMissingRole'].format(player=player.mention),
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif error == 'AlreadyVoted':  # Уже проголосовал за данного прикола
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Vote AlreadyVoted'].format(player=player.mention),
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif error == 'BadArgument':  # Какую-то хуйню вместо аргументов указал
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Vote BadArgument'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif error == 'SelfVoting':  # Голосование за самого себя
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Vote SelfVoting'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif error == 'Cooldown':  # КД
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Vote Cooldown'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)

    elif error == 'TooFewHours':  # Недостаточно часов
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Vote TooFewHours'].format(hours=config['hours_to_vote']),
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    else:
        print(error)


@bot.command()
async def unvote(ctx, player=None):
    if not channel_check(ctx):
        return 'Pepega'
    if player == ctx.author:
        await vote_error(ctx, error='SelfVoting')
        return None

    if ctx.author.guild.get_role(config['fvote_role']) in ctx.author.roles and player is not None:
        player = get_player_by_str(ctx, player)
        if player is None:
            await unvote_error(ctx, error='BadArgument')
            return None
        member = player
        cooldown_ignoring = True
    elif player is not None:
        await unvote_error(ctx, 'Dolbaeb')
        return None
    else:
        cooldown_ignoring = False
        member = ctx.author

    vote = db.select(columns='voted_user, last_vote_timestamp', where=f'discord_id = {member.id}')
    if vote is not None:
        if vote[1] + config['vote_cooldown'] > time.time() and not cooldown_ignoring:
            await unvote_error(ctx, 'Cooldown')
            return False
        db.delete(where=f'discord_id={member.id}')
        await update_member(Pguild.get_member(int(vote[0])))

    else:
        await unvote_error(ctx, 'NoSuchVote', player=member)
        return None

    await logger(ctx=ctx, type='unvoted', player1=member)


@unvote.error
async def unvote_error(ctx, error, player=None):
    if not channel_check(ctx):
        return 'Pepega'
    if error == 'NoSuchVote':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Unvote NoSuchVote'].format(player=player.mention),
                              colour=errors['err_colour'])
        await ctx.send(ctx.author.mention, embed=embed)
    elif error == 'Dolbaeb':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Unvote Dolbaeb'],
                              colour=errors['err_colour'])
        await ctx.send(ctx.author.mention, embed=embed)
    elif error == 'Cooldown':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Unvote Cooldown'],
                              colour=errors['err_colour'])
        await ctx.send(ctx.author.mention, embed=embed)
    elif error == 'BadArgument':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Unvote BadArgument'],
                              colour=errors['err_colour'])
        await ctx.send(ctx.author.mention, embed=embed)
    else:
        await ctx.send(error)


@bot.command()
@commands.has_role(config['fvote_role'])
async def fvote(ctx, player1, player2):
    player1 = get_player_by_str(ctx, player1)
    player2 = get_player_by_str(ctx, player2)

    if player2 is None or player1 is None:
        await fvote_error(ctx, error='playerNotFound')
        return None
    if player_role not in player1.roles:
        await fvote_error(ctx, error='playerMissingRole', dolbaeb=player1)
        return None
    if player_role not in player2.roles:
        await fvote_error(ctx, error='playerMissingRole', dolbaeb=player2)
        return None
    if player1 == player2:
        await fvote_error(ctx, error='SelfVoting')
        return None
    if get_played_hours(player1.id) < config['hours_to_vote']:
        await fvote_error(ctx, error='TooFewHours', dolbaeb=player1)
        return None

    AV = False
    vote = db.select(columns='voted_user, last_vote_timestamp', where=f'discord_id = {player1.id}')
    if vote is not None:
        if vote[1] + config['vote_cooldown'] > time.time():
            # кд
            return False
        if int(vote[0]) == player2.id:
            await fvote_error(ctx, 'AlreadyVoted', dolbaeb=player2, author=player1)
            return False
        db.update(data=f'voted_user = {player2.id}, last_vote_timestamp={int(time.time())}',
                  where=f'discord_id={player1.id}')
        AV = True

    else:
        db.insert(
            data=f'id=NULL, discord_id={player1.id},voted_user={player2.id}, last_vote_timestamp={int(time.time())}')

    if AV:
        await update_member(Pguild.get_member(int(vote[0])))
    await update_member(player2)
    await logger(ctx, type='fvoted', player1=player1, player2=player2)


@fvote.error
async def fvote_error(ctx, error, dolbaeb=None, author=None):
    if not channel_check(ctx):
        return 'Pepega'
    if isinstance(error, commands.errors.MissingRole):
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Fvote MissingRole'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Fvote MissingRequiredArgument'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif error == 'playerMissingRole':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Fvote PlayerMissingRole'].format(player=dolbaeb.mention),
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif error == 'AlreadyVoted':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Fvote AlreadyVoted'].format(player1=author.mention,
                                                                              player2=dolbaeb.mention),
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif error == 'playerNotFound':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Fvote playerNotFound'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif error == 'SelfVoting':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Fvote SelfVoting'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif error == 'TooFewHours':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['Fvote TooFewHours'].format(player1=dolbaeb.mention,
                                                                             hours=config['hours_to_vote']),
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    else:
        await ctx.send(error)


@bot.command(name='vote-info')
async def vote_info(ctx, player=None):
    if not channel_check(ctx):
        return
    if player is None:
        player = ctx.author
    else:
        player = get_player_by_str(ctx, player)
        if player is None:
            await vote_info_error(ctx, error='BadArgument')
            return None
    voted = get_votes(player.id, return_users=True)

    voted_for = db.select(columns='voted_user', where=f'discord_id = {player.id}')
    title = f'Статистика  {player.display_name} {config["votes_emoji"] if len(voted) >= config["votes_to_member"] else ""}'
    if voted_for is None:
        embed = discord.Embed(title=title,
                              description='Пользователь ни за кого не проголосовал',
                              colour=0x11FF00)
    else:
        embed = discord.Embed(title=title,
                              description=f'Пользователь проголосовал за {"<@" + voted_for[0] + ">"}',
                              colour=0x11FF00)

    if len(voted) > 0:
        users = ''
        for user in voted:
            users += " " + '<@' + user + ">"
        embed.add_field(name=f'За {player.display_name} проголосовало: **{len(voted)}**', value=users)

    embed.set_thumbnail(url=f'https://rp.plo.su/avatar/{player.display_name}')

    await ctx.send(f'{ctx.author.mention}', embed=embed)



@vote_info.error
async def vote_info_error(ctx, error):
    if not channel_check(ctx):
        return 'Pepega'
    if error == 'BadArgument':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['vote-info BadArgument'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    else:
        print(error)


@bot.command(name='vote-rcd')
@commands.has_role(config['fvote_role'])
async def vote_rcd(ctx, player='хуй'):
    if not channel_check(ctx):
        return 'Pepega'
    if player == 'хуй':
        player = ctx.author
    else:
        player = get_player_by_str(ctx, player)
        if player is None:
            await vote_rcd_error(ctx, 'BadArgument')
            return None

    vote = db.select(columns='last_vote_timestamp', where=f'discord_id = {player.id}')
    if vote is not None:
        if vote[0] + config['vote_cooldown'] <= time.time():
            await vote_rcd_error(ctx, 'NoCooldown')
            return False
        db.update(where=f'discord_id={player.id}', data='last_vote_timestamp=0')
        print(vote)

    else:
        await vote_rcd_error(ctx, 'NoCooldown')
        return None

    await logger(ctx=ctx, type='rcd', player1=player)


@vote_rcd.error
async def vote_rcd_error(ctx, error):
    if not channel_check(ctx):
        return 'Pepega'

    if isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['rcd MissingRequiredArgument'],
                              colour=errors['err_colour'])
        await ctx.send(ctx.author.mention, embed=embed)
    elif isinstance(error, commands.errors.MissingRole):
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['rcd MissingRole'],
                              colour=errors['err_colour'])
        await ctx.send(ctx.author.mention, embed=embed)
    elif error == 'NoCooldown':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['rcd NoCooldown'],
                              colour=errors['err_colour'])
        await ctx.send(ctx.author.mention, embed=embed)

    elif error == 'BadArgument':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['rcd BadArgument'],
                              colour=errors['err_colour'])
        await ctx.send(ctx.author.mention, embed=embed)
    else:
        await ctx.send(error)


# TODO: !vote-top
@bot.command(name='vote-top')
@commands.has_role(config['player'])
@commands.cooldown(rate=1, per=config['vote_top_cooldown'], type=commands.BucketType.user)
async def vote_top(ctx):
    if not channel_check(ctx):
        return 'Pepega'

    top_list = top()
    vt_len = config['vote_top_len']

    if len(top()) == 0:
        await vote_top_error(ctx, 'DatabaseCleared')
        return None

    embed = discord.Embed(title=texts['vote_top_title'], colour=texts['err_color'])
    num = 1
    for user in top_list:
        if num <= vt_len:
            name = f'{num}. {Pguild.get_member(user[1]).display_name} {config["votes_emoji"] if get_votes(user[1]) >= config["votes_to_member"] else ""}'
            votes = get_votes(user[1])
            value = f'{votes} голос'
            if str(votes)[-1:] in ["5", "6", "7", "8", "9"]:
                value += "oв"
            elif str(votes)[-1:] in ["2", "3", "4"]:
                value += 'а'

            embed.add_field(name=name, value=value, inline=True)
        num += 1
    message = await ctx.send(f'{ctx.author.mention}', embed=embed)
    #rn = bot.get_emoji(config['reaction_next'])
    #await message.add_reaction(rn)
    #await message.add_reaction(bot.get_emoji(config['reaction_reload']))
    #await message.add_reaction(bot.get_emoji(config['reaction_previous']))


@vote_top.error
async def vote_top_error(ctx, error):
    if error == 'DatabaseCleared':
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['vote-top DatabaseCleared'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif isinstance(error, commands.errors.MissingRole):
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['vote-top MissingRole'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    elif isinstance(error, commands.errors.CommandOnCooldown):
        embed = discord.Embed(title=errors['err_title'],
                              description=errors['vote-top CommandOnCooldown'],
                              colour=errors['err_colour'])
        await ctx.send(f'{ctx.author.mention}', embed=embed)
    else:
        print(error)


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(config['activity']))

    global Pguild, player_role, member_role, aLogs, pLogs, member_role
    Pguild = bot.get_guild(config['guild_id'])
    player_role = Pguild.get_role(config['player'])
    member_role = Pguild.get_role(config['parliament_member_role'])
    pLogs = bot.get_channel(config['publicLogs'])
    aLogs = bot.get_channel(config['roflanEbaloLogs'])
    member_role = Pguild.get_role(config['parliament_member_role'])
    scheduler = AsyncIOScheduler()
    autoUpdater(scheduler)
    scheduler.start()

    print('Connected...')
    await update_members()


if __name__ == '__main__':
    bot.run(config['token'])
