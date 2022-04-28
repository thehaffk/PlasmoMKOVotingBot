import os

from dotenv import load_dotenv

from mkovotebot.settings import DEBUG


load_dotenv()

TOKEN = os.getenv("TOKEN")


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


class TestServer:
    """
    Test Config for Plasmo RP Discord Guild
    """

    id = 966785796902363188

    admin_role_id = 966785796927524897
    mko_head_role_id = 966785796902363194
    mko_member_role_id = 969284288229044245
    player_role_id = 966785796902363189

    fvote_role_id = mko_head_role_id

    announcement_channel_id = 956990708164747264


if DEBUG:
    PlasmoRPGuild = TestServer


class DevServer:
    """
    Config for development server (digital drugs technologies)
    """

    pass  # TODO: Error logger
