__version__ = "2.0.0a"

DEBUG = True
DATABASE_PATH = "mkovotebot/votes.db"


class Config:
    mko_voting_enabled = True

    # ⚠ mko_voting_enabled must be True for using this
    user_voting_enabled = (
        True  # Allows players to vote with /vote, instead of in-game books
    )
    vote_cooldown = 24  # In hours

    president_voting_enabled = True  # Enables president elections (commands and checks)
    # ⚠ mko_voting_enabled must be True for using this
    # president_user_voting_enabled = (
    #     True  # Allows players to vote with /pvote, instead of in-game books
    # )

    required_weekly_hours = 1
    required_mko_votes = 2

    member_emoji = "\\🏛"

    dynamic_voting_enabled = False  # todo
    minimum_members = 10
    maximum_members = 25
    minimum_required_votes = 1
    maximum_required_votes = 10
