from dataclasses import dataclass
from functools import lru_cache
from typing import Optional, Union

import aiohttp


@dataclass
class Player:
    plasmo_id: int
    discord_id: int
    nick: str


# TODO: Rename this
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
        raise ValueError("All three parameters are None")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://plasmorp.com/api/user/profile?" + user_string + "&fields=stats"
        ) as response:
            if response.status != 200:
                return None
            response_json = await response.json()
            if not response_json.get("status", False):
                return None
            data = response_json["data"]

            return _Player(
                plasmo_id=data["id"],
                discord_id=int(data["discord_id"]),
                nick=data["nick"],
                weekly_hours=data["stats"]["week"] // 60 / 60,
            )


async def get_player_hours(discord_id: int) -> float:
    user = await _get_plasmo_userdata(discord_id=discord_id)
    if user is None:
        return -1
    else:
        return user.weekly_hours


@lru_cache(maxsize=256)
async def get_user(
    plasmo_id: int = None, discord_id: int = None, nickname: str = None
) -> Union[None, Player]:
    player = await _get_plasmo_userdata(plasmo_id, discord_id, nickname)
    if player is None:
        return None
    else:
        player: _Player
        return Player(
            plasmo_id=player.plasmo_id, discord_id=player.discord_id, nick=player.nick
        )
