from dataclasses import dataclass


@dataclass
class Player:
    plasmo_id: int
    discord_id: int
    nick: str
    weekly_hours: float


async def get_user(
    plasmo_id: int = None, discord_id: int = None, nickname: str = None
) -> Player:
    ...
    return Player(
        plasmo_id=433,
        discord_id=737501414141591594,
        nick="_howkawgew",
        weekly_hours=12.3,
    )  # Test data
