
#CONFIG


### Основное

`token`	 						Токен бота\
`prefix`							Префикс бота\
`activity`						Игровая активность бота\
`admins`							Список администраторов бота(-кд)

### Настройки
`guild_id`						id гильды (Plasmo RP)\
`player` 							id роли игрок\
`fvote_role`						id роли для fvote\
`parliament_member_role`			id роли члена парламента


### Часы
`hours_to_vote`					Должно быть наиграно у игрока часов чтобы он смог проголосовать\


### Каналы
`trusted`						Каналы в которых бот реагирует на команды. (Защита от спама, например в #игра)\
`publicLogs`						Важные логи. Пользователь вступил в парламент, покинул.\
`roflanEbaloLogs`					Посредственные логи. (Голос снят за неактив)


### Настройки парламента
**Динамически подбирает нужное количество голосов чтобы количество участников не превышало dynamic_votes_max**\
`dynamic_votes`					Включить/Выключить динамический подбор количества голосов для попадания в парламент \
`dynamic_votes_max`				Максимальное количество участников парламента

`votes_to_member`					Нужно набрать голосов чтобы стать членом парламента \
`votes_emoji`						Рофлан эмоут для вывода в топ/стату состояния о наличии в парламенте


`vote_cooldown`					Кулдаун изменения голоса





# Тексты

`voted_title `  
`voted_desk `  
`voted_color `

`fvoted_title `  
`fvoted_desk `   
`fvoted_color `

`unvote_title `   
`unvote_desk `  
`unvote_color `


`err_title `  
`err_colour `

### Описание ошибок
!vote errors\
`Vote MissingRole `  			У пользователя нет роли игрока\
`Vote MissingRequiredArgument `	Команда была вызвана без аргументов\
`Vote PlayerMissingRole ` 		Пользователь в аргументах - не игрок\
`Vote AlreadyVoted ` 			Голос игрока и так отдан за игрока указанного в аргумента\
`Vote BadArgument ` 				Игрок указал что-то непонятное в аргументах\
`Vote SelfVoting ` 				Игрок голосует сам за себя\
`Vote Cooldown ` 				У игрока кулдаун изменения голоса\
`Vote TooFewHours ` 				У игрока недостаточно часов наиграно за неделю
!fvote  \
`Fvote MissingRole `				Команду вызвал игрок без роли на нее\
`Fvote MissingRequiredArgument `	Команда вызвана без аргументов\
`Fvote PlayerMissingRole `		У одного из игроков нет роли игрока\
`Fvote AlreadyVoted `			Игрок1 уже проголосовал за игрока2\
`Fvote BadArgument `				Указано что-то непонятное в аргументах \
`Fvote SelfVoting` 				Указан один и тот же игрок\
`Fvote TooFewHours`				У игрока недостаточно часов наиграно за неделю
