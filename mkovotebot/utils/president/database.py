from __future__ import annotations

from dataclasses import dataclass
from typing import List

from mkovotebot.utils.internal.database import MKODatabase


class PresidentElectionsDatabase(MKODatabase):
    def __init__(self):
        super().__init__(table="mko")
