from typing import List

from mkovotebot.utils.models import MKOVote, PresidentVote


class Candidate:
    def __init__(self, discord_id, votes_count):
        self.discord_id = discord_id
        self.votes_count = votes_count


async def get_mko_candidates() -> List[Candidate]:
    """
    Get list of all MKO candidates
    """
    all_votes = await MKOVote.objects.all()
    candidates_ids = set([vote.candidate_id for vote in all_votes])
    candidates = []

    for candidate_id in candidates_ids:
        candidates.append(
            Candidate(
                discord_id=candidate_id,
                votes_count=len(
                    [vote for vote in all_votes if vote.candidate_id == candidate_id]
                ),
            )
        )

    return sorted(candidates, reverse=True, key=lambda i: i.votes_count)

async def get_election_candidates() -> List[Candidate]:
    """
    Get list of all candidates in president elections
    """
    all_votes = await PresidentVote.objects.all()
    candidates_ids = set([vote.candidate_id for vote in all_votes])
    candidates = []

    for candidate_id in candidates_ids:
        candidates.append(
            Candidate(
                discord_id=candidate_id,
                votes_count=len(
                    [vote for vote in all_votes if vote.candidate_id == candidate_id]
                ),
            )
        )

    return sorted(candidates, reverse=True, key=lambda i: i.votes_count)
