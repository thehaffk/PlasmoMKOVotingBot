import logging

import databases
import orm

from mkovotebot import settings

database = databases.Database("sqlite:///" + settings.DATABASE_PATH)
models = orm.ModelRegistry(database)

logger = logging.getLogger(__name__)


class MKOVote(orm.Model):
    tablename = "mko_votes"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "voter_id": orm.BigInteger(unique=True),
        "candidate_id": orm.Integer(allow_null=False),
    }


class PresidentVote(orm.Model):
    tablename = "election_votes"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "voter_id": orm.BigInteger(unique=True),
        "candidate_id": orm.Integer(allow_null=False),
    }


class Cooldown(orm.Model):
    tablename = "cooldowns"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "voter_id": orm.BigInteger(unique=True),
        "mko_cooldown": orm.BigInteger(default=0),
        "elections_cooldown": orm.BigInteger(default=0),
    }


async def setup_models():
    logger.info("Creating tables")
    await models.create_all()
