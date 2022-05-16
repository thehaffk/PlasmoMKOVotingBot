from dataclasses import dataclass

import asyncio
from functools import lru_cache
from typing import Union, Optional

import aiohttp


@dataclass
class Player:
    plasmo_id: int
    discord_id: int
    nick: str


@dataclass
class _Player(Player):
    weekly_hours: float


async def _get_plasmo_userdata(
    plasmo_id: int = None, discord_id: int = None, nickname: str = None
) -> Optional[_Player]:
    if plasmo_id:
        user_string = "id=" + str(plasmo_id)
    elif discord_id:
        user_string = "discord_id=" + str(discord_id)
    elif nickname:
        user_string = "nick=" + str(nickname)
    else:
        raise ValueError("All three parameters cannot be None")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://rp.plo.su/api/user/profile?" + user_string + "&fields=stats"
        ) as response:
            if response.status != 200:
                return None
            response_json = await response.json()
            if (
                not response_json.get("status", False)
                or response_json.get("data", {}).get("on_server", False) is False
            ):
                return None
            data = response_json["data"]

            return _Player(
                plasmo_id=data["id"],
                discord_id=int(data["discord_id"]),
                nick=data["nick"],
                weekly_hours=data["stats"]["week"] // 60 / 60,
            )


async def get_player_hours(plasmo_id: int):
    user = await _get_plasmo_userdata(plasmo_id=plasmo_id)
    if user is None:
        return 0
    else:
        return user.weekly_hours


@lru_cache(maxsize=128)
async def get_user(
    plasmo_id: int = None, discord_id: int = None, nickname: str = None
) -> Union[None, Player]:
    player = await _get_plasmo_userdata(plasmo_id, discord_id, nickname)
    if player is None:
        player: None
        return None
    else:
        # looks terrible, there must be some smart way to do it
        player: _Player
        return Player(
            plasmo_id=player.plasmo_id, discord_id=player.discord_id, nick=player.nick
        )