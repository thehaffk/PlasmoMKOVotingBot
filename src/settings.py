config = {

    'token': 'ODQyNDgzNDQ0MzMxOTcwNTYw.YJ192Q.VNDPsianrDhpfE73s_itlasV45s',
    'prefix': '!',
    'activity': 'Plasmo MKO by _howkawgew',
    'admins': [191836876980748298, 737501414141591594, 222718720127139840],


    # Роли
    'guild_id': 828683007635488809,  # rp: 672312131760291842
    'player': 841098135376101377,  # rp: 746628733452025866
    'fvote_role': 842481508366417950,  # rp совет_глав: 810492714235723777 | rp админ: 704364763248984145
    'parliament_member_role': 843149927953596436,  # rp: ???? Pepega


    # Часы
    'hours_to_vote': 0,


    # Каналы
    'private_voting': True,  # Only fvoters can vote
    'channel_filtering': True,
    'trusted': [828683027541917697, ],

    'publicLogs': 842484261180669962,  # Parliament join/leave
    'roflanEbaloLogs': 843164835122511872,  # Vote rejected

    'dynamic_votes': False,  # Удалил потому что сроки поджимают peepoClown
    'dynamic_votes_max': 20,

    'votes_to_member': 3,  # Нужно голосов чтобы стать parliament_member
    'votes_emoji': ':classical_building:',  # Смайлик епта

    'vote_cooldown': 60,  # В СЕКУНДАХ! кулдаун команды
    # 1час -> 3600
    # 4 часа -> 14400
    # 12 часов -> 43200
    # 24 часа -> 86400
    # 2 дня -> 172800

    'vote_top_len': 9,

    'reaction_previous': '⬅️',
    'reaction_reload': '',
    'reaction_next': '➡️',

    'vote_top_cooldown': 10,

}

texts = {

    'voted_title': 'Голос засчитан',
    'voted_desk': '{player1} проголосовал за {player2}',
    'voted_color': 0x00FF00,

    'fvoted_title': 'Голос изменен',
    'fvoted_desk': 'Голос {player1} отдан игроку {player2}',
    'fvoted_color': 0x00FF00,

    'unvoted_title': 'Голос сброшен',
    'unvoted_desk': 'Голос {player1} был сброшен',
    'unvoted_color': 0x00FF00,

    'added_pmember_title': 'Новый участник совета',
    'added_pmember_desk': '{player1} прошел в совет',
    'added_pmember_color': 0x00FF00,

    'removed_pmember_title': 'Игрок покидает совет',
    'removed_pmember_desk': '{player1} потерял голоса нужные для участия в совете',
    'removed_pmember_color': 0xFF0000,

    'rejected_vote_title': 'Ваш голос аннулирован',
    'rejected_vote_desk': 'Чтобы голосовать нужно наиграть хотя бы {hours} часов за неделю',
    'rejected_vote_color': 0xFF0000,

    'rcd_title': 'Кулдаун обнулен',
    'rcd_desk': 'Кулдаун у {player} сброшен',
    'rcd_color': 0x00FF00,

    'vote_top_title': 'Топ игроков по голосам',
    'err_color': 0x00FF00,

}

errors = {
    # Описание любого непонятного пункта в конфиге есть в README Pepega

    'err_title': '',
    'err_colour': 0xFF0000,
    # пинг вне эмбеда во всех ошибках
    'Vote MissingRole': 'Боже чел ты чухан, у тебя даже роли игрока нет',
    'Vote PlayerMissingRole': 'Ну и долбаеба ты выбрал, у {player} даже роли игрока нет нахуй',
    'Vote AlreadyVoted': 'У тебя склероз нахуй? Ты уже проголосовал за {player}',
    'Vote SelfVoting': 'Блять еще один. Тебе совсем делать нехуй, уебище? Нахуя ты за себя голосуешь?',
    'Vote Cooldown': 'Да пососи блять, у тебя еще кд не прошел, лох',
    'Vote TooFewHours': 'Ахах блять, ты тут проходом ебать? У тебя даже {hours} часов на плазме нет',

    'Fvote MissingRole': 'У тебя роль для fvote есть? нет? ну тогда нахуй ты это написал?',
    'Fvote PlayerMissingRole': 'Ну и долбаеба ты выбрал, у {player} даже роли игрока нет нахуй',
    'Fvote AlreadyVoted': 'Как такое вообще можно не знать? {player1} уже проголосовал за {player2}',
    'Fvote SelfVoting': 'Блять еще один. Тебе совсем делать нехуй? Путин тоже сам за себя голосовал? а стоп...',
    'Fvote TooFewHours': 'Ахах блять, он тут проходом ебать? У {player1} даже {hours} часов на плазме нет',

    'Unvote NoSuchVote': 'Чел ты... {player} ни за кого не голосовал...',
    'Unvote Dolbaeb': 'Долбаеб',
    'Unvote Cooldown': 'Жесть чел у тебя еще кулдаун блин!!!',

    'rcd MissingRole': 'Ты кто такой чтобы это делать?',
    'rcd NoCooldown': 'У игрока нет кулдауна, ты дурак?',

    'vote-top DatabaseCleared': 'В базе данных... 0 строк?',
    'vote-top MissingRole': 'Ты даже не игрок',
    'vote-top CommandOnCooldown': 'Кулдаун',

}
