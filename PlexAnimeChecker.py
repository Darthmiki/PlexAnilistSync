import re
import logging

from PlexAnimeHelper import PlexAnimeHelper


LOGGER = logging.getLogger(__name__)


def check_plex_anime(plex_username, plex_password, plex_server_dict):
    
    plex_anime_helper = PlexAnimeHelper(
        plex_username,
        plex_password,
        plex_server_dict,
    )
    plex_entries = []
    for server in plex_server_dict.keys():
        for section in plex_server_dict[server]:
            plex_entries.extend(plex_anime_helper.get_all_shows(server, section))

    LOGGER.info("Checking if plex anime entries are anidb:")
    for entry in plex_entries:
        if not re.search("(?<=anidb-)\d+", entry.guid):
            LOGGER.warning("%s - %s",entry.title, entry.guid)
    LOGGER.info("*****************************************")
    LOGGER.info("Looking for merged entries:")
    for entry in plex_entries:
        if len(entry.locations) > 1:
            LOGGER.warning("%s - %s", entry.title, entry.locations)
    LOGGER.info("Check complete")
