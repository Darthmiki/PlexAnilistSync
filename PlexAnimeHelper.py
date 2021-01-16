import logging

from plexapi.myplex import MyPlexAccount
from plexapi.video import Movie

class PlexAnimeHelper:
    def __init__(self, username, password, servers):
        self.myPlexAccount = self.authenticate(username, password)
        self.servers = {}
        for s in servers:
            self.servers[s] = self.myPlexAccount.resource(s).connect()

    def authenticate(self, username, password):
        return MyPlexAccount(username, password)

    def get_shows_with_watched_episodes(self, server, section):
        section = self.servers[server].library.section(section)
        return section.search(**{"episode.unwatched": False})

    def get_watched_episodes(self, plex_entry):
        if isinstance(plex_entry, Movie):
            return 1 if plex_entry.isWatched else 0
        else:
            return len([episode for episode in plex_entry.watched() if episode.seasonNumber != 0])

    def refresh_section(self, server, section):
        section = self.servers[server].library.section(section)
        section.update()