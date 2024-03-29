import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DEBUG_VALUES = bool(int(os.getenv("DEBUG_VALUES", False)))

maximum_candidates_per_page = 10


class PlasmoRPGuild:
    """
    Config for Plasmo RP Discord Guild
    """

    id = 672312131760291842

    admin_role_id = 704364763248984145
    mko_head_role_id = 810492714235723777
    mko_member_role_id = 844507728671277106
    player_role_id = 746628733452025866

    fvote_role_id = mko_head_role_id

    announcement_channel_id = 844505711211446282
    low_priority_announcement_channel_id = 754644298720477264


class MKOStructureGuild:
    id = 814490777526075433
    invite_url = "https://discord.gg/YwRDyBCAJD"


class TestServer:
    """
    Test Config for Plasmo RP Discord Guild
    """

    id = 966785796902363188

    admin_role_id = 966785796927524897
    mko_head_role_id = 966785796902363194
    mko_member_role_id = 1001980910842945606
    player_role_id = 966785796902363189

    fvote_role_id = mko_head_role_id

    announcement_channel_id = 969280776459935884
    low_priority_announcement_channel_id = 969291098348458004


if DEBUG_VALUES:
    PlasmoRPGuild = TestServer


class DevServer:
    """
    Config for development server (digital drugs technologies)
    """

    id = 966785796902363188
    log_channel_id = 976077504718712832
    pass  # TODO: Error logger
