__version__ = "2.0.0a"

DEBUG = True
DATABASE_PATH = "mkovotebot/votes.db"


class Config:
    mko_voting_enabled = True

    # ⚠ mko_voting_enabled must be True for using this
    user_voting_enabled = False  # Allows players to vote with /vote, instead of in-game books

    vote_cooldown = 60  # In minutes

    president_voting_enabled = True  # Enables president elections (commands and checks)

    required_weekly_hours = 100
    required_mko_votes = 2

    member_emoji = "\\🏛"

    # TODO
    dynamic_voting_enabled = False  # MKO ONLY
    minimum_members = 10
    maximum_members = 25
    minimum_required_votes = 1
    maximum_required_votes = 10
