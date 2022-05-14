from __future__ import annotations

from dataclasses import dataclass
from typing import List

import aiosqlite as aiosqlite

from mkovotebot import settings

PATH = settings.DATABASE_PATH


@dataclass
class Candidate:
    plasmo_id: int
    votes_count: int


class MKODatabase:
    def __init__(self, table: str):
        if table not in ["mko_votes", "president_votes"]:
            raise ValueError(f"{table} table is not allowed")
        self.table = table

    async def setup(self):
        """
        Create database if not exist
        :return:
        """
        query = """
        CREATE TABLE IF NOT EXISTS ?
        (
            voter_id     integer not null,
            candidate_id integer not null
        );

        create unique index president_votes_voter_id_uindex
            on ? (voter_id);
        """
        async with aiosqlite.connect(PATH) as db:
            await db.execute(query, (self.table, self.table))
            await db.commit()

    async def set_user_vote(
        self, voter_plasmo_id: int, candidate_plasmo_id: int | None
    ):
        async with aiosqlite.connect(PATH) as db:
            if candidate_plasmo_id is not None:
                await db.execute(
                    """INSERT INTO ?(voter_id, candidate_id) VALUES(?, ?)
           ON CONFLICT(voter_id) DO UPDATE SET candidate_id=?""",
                    (
                        self.table,
                        voter_plasmo_id,
                        candidate_plasmo_id,
                        candidate_plasmo_id,
                    ),
                )
            else:
                await db.execute(
                    """DELETE FROM ? WHERE voter_id = ?""",
                    (self.table, voter_plasmo_id),
                )

            await db.commit()
        return True

    async def reset_candidate_votes(self, candidate_plasmo_id: int) -> List[int]:
        candidate_votes = await self.get_candidate_votes(candidate_plasmo_id)
        async with aiosqlite.connect(PATH) as db:
            await db.execute(
                """DELETE FROM ? WHERE candidate_id = ?""",
                (self.table, candidate_plasmo_id),
            )

            await db.commit()
        return candidate_votes

    async def get_user_vote(self, voter_plasmo_id: int) -> int:
        ...  # TODO

    async def get_candidate_votes(self, candidate_plasmo_id: int) -> List[int]:
        ...  # TODO
        return [4]

    async def get_candidates(self, sort_descending=False) -> List[Candidate]:
        ...  # TODO
        return [Candidate(plasmo_id=433, votes_count=5)]


class PresidentElectionsDatabase(MKODatabase):
    def __init__(self):
        super().__init__(table="president_votes")


class MKOVotingDatabase(MKODatabase):
    def __init__(self):
        super().__init__(table="mko_votes")
