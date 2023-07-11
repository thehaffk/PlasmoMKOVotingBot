def get_votes_string(votes_count: int) -> str:
    if votes_count % 100 in [11, 12, 13, 14]:
        return str(votes_count) + " голосов"
    endings_dict = {1: "голос", 2: "голоса", 3: "голоса", 4: "голоса"}
    return str(votes_count) + " " + endings_dict.get(votes_count % 10, "голосов")
