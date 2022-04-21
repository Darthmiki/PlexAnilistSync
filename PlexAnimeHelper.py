import logging
import re

from plexapi.myplex import MyPlexAccount
from plexapi.video import Movie

LOGGER = logging.getLogger(__name__)


class PlexAnimeHelper:
    def __init__(self, username, password, servers):
        self.myPlexAccount = self.authenticate(username, password)
        self.servers = {}
        for s in servers:
            self.servers[s] = self.myPlexAccount.resource(s).connect()

    def authenticate(self, username, password):
        return MyPlexAccount(username, password)

    def get_shows_with_watched_episodes(self, server_name, section_name=None):
        section = self.servers[server_name].library.section(section_name)
        try:
            return section.search(**{"episode.unwatched": False})
        except:
            return [
                plex_entry
                for plex_entry in section.search()
                if self.get_watched_episodes(plex_entry)
            ]

    def get_watched_episodes(self, plex_entry):
        if isinstance(plex_entry, Movie):
            return 1 if plex_entry.isWatched else 0
        else:
            return len(
                [
                    episode
                    for episode in plex_entry.watched()
                    if episode.seasonNumber != 0
                ]
            )

    def get_all_shows(self, server_name, section_name):
        section = self.servers[server_name].library.section(section_name)
        return section.all()

    def refresh_section(self, server, section):
        section = self.servers[server].library.section(section)
        section.update()

    def check_anidb_mapping(self, server_name, section_name):
        section = self.servers[server_name].library.section(section_name)
        count = 0
        for entry in section.all():
            anidb_id = re.search("(?<=anidb-)\d+", entry.guid)
            if not anidb_id:
                LOGGER.warning("Missing anidbId: %s", entry.title)
                count += 1
        LOGGER.info("Check complete. Missing anidbId in %s Plex entries", count)
