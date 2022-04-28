from __future__ import annotations

from dataclasses import dataclass
from typing import List

from mkovotebot.utils.internal.database import *


@dataclass
class Candidate:
    plasmo_id: int
    votes_count: int


# TODO: Docstrings
class MKOVotingDatabase(MKODatabase):
    def __init__(self):
        super().__init__(table="president")