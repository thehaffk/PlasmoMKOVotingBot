import logging

import disnake
from disnake.ext import commands

from mkovotebot import config

logger = logging.getLogger()


class MKOVoteBot(commands.Bot):
    """
    Base bot instance.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def create(cls) -> "MKOVoteBot":
        """Create and return an instance of a Bot."""
        _intents = disnake.Intents.none()
        _intents.members = True
        _intents.guilds = True

        return cls(
            owner_ids=[737501414141591594, 222718720127139840, 191836876980748298],
            status=disnake.Status.do_not_disturb,
            intents=_intents,
            command_prefix=commands.when_mentioned,
            allowed_mentions=disnake.AllowedMentions(everyone=False),
            test_guilds=[config.PlasmoRPGuild.id],
            activity=disnake.Game(
                name="Bot for MKO voting and president elections,"
                " made by digital drugs technologies"
            ),
        )
