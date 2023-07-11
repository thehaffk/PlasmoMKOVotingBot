import os

from dotenv import load_dotenv

load_dotenv()

__version__ = "2.1.0"

DEBUG = bool(int(os.getenv("BOT_DEBUG", False)))
DATABASE_PATH = "mkovotebot/votes.db"


class Config:
    mko_voting_enabled = bool(int(os.getenv("MKO_VOTING", True)))

    user_voting_enabled = bool(
        int(os.getenv("MKO_USER_VOTING", False))
    )  # Allows players to vote with /vote
    vote_cooldown = 24  # In hours
    vote_cooldown += 3  # I have no idea whats wrong with datetime.utcnow().timestamp() + i dont care

    president_voting_enabled = bool(
        int(os.getenv("PRESIDENT_VOTING", False))
    )  # Enables president elections (commands and checks)
    # ⚠ mko_voting_enabled must be True for using this
    # president_user_voting_enabled = (
    #     bool(int(os.getenv("PRESIDENT_USER_VOTING", False)))  # Allows players to vote with /pvote
    # )

    required_weekly_hours = int(os.getenv("MKO_WEEKLY_HOURS", 1))
    required_mko_votes = int(os.getenv("MKO_VOTES", 6))

    member_emoji = "\\🏛"

    # dynamic_voting_enabled = False  # todo
    # minimum_members = 10
    # maximum_members = 25
    # minimum_required_votes = 1
    # maximum_required_votes = 10
