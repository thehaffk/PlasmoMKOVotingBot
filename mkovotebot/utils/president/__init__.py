from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Candidate:
    plasmo_id: int
    votes_count: int


# TODO: Docstrings


async def set_user_vote(voter_plasmo_id: int, candidate_plasmo_id: int | None):
    ...  # TODO
    return


async def reset_candidate_votes(candidate_plasmo_id: int) -> int:
    ...  # TODO
    return 1


async def get_user_vote(voter_plasmo_id: int) -> int:
    ...  # TODO


async def get_candidate_votes(candidate_plasmo_id: int) -> int:
    ...  # TODO
    return 4


async def get_candidates(sort_descending=False) -> List[Candidate]:
    ...  # TODO
    return [Candidate(plasmo_id=433, votes_count=5)]
