import requests
import simplejson
import pathlib
import datetime
import os
import re
import logging

from lxml import etree

ANIME_DB_REFRESH_IN_DAYS = int(os.getenv("ANIME_DB_REFRESH_IN_DAYS", 7))

MANAMI_PROJECT_DB_URL = "https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database.json"
MANAMI_PROJECT_FILE = "anime-offline-database.json"

TVDB_ANIDB_ANIME_LIST_URL = (
    "https://raw.githubusercontent.com/Anime-Lists/anime-lists/master/anime-list.xml"
)
TVDB_ANIDB_ANIME_LIST_FILE = "anime-list.xml"

LOGGER = logging.getLogger(__name__)


class PlexAnilistMatcher:
    def __init__(self) -> None:
        self.get_anidb_anilist_mapping()
        self.get_tvdb_anidb_mapping()

    def map_plex_guid_to_anilist_id(self, plex_guid):
        if (
            not self.file_age
            or self.file_age
            < (datetime.datetime.utcnow()
            + datetime.timedelta(days=-ANIME_DB_REFRESH_IN_DAYS))
        ):
            self.get_anidb_anilist_mapping()
            self.get_tvdb_anidb_mapping()
        anidb_id = re.search("(?<=anidb-)\d+", plex_guid)
        if anidb_id:
            return self.anidb_anilist_mapping.get(anidb_id.group(0))
        tvdb_id = re.search("(?<=tvdb-)\d+", plex_guid)
        if tvdb_id:
            LOGGER.warning(
                "Possible repeated entry in db. If possible change Plex match to anidb"
            )
            return self.anidb_anilist_mapping.get(
                self.tvdb_anidb_mapping.get((tvdb_id.group(0)))
            )
        return None

    def get_anidb_anilist_mapping(self):
        p = pathlib.Path(MANAMI_PROJECT_FILE)
        self.download_file(MANAMI_PROJECT_DB_URL, MANAMI_PROJECT_FILE)
        self.file_age = datetime.datetime.fromtimestamp(p.stat().st_mtime)
        with p.open("rb") as f:
            anime_list = simplejson.load(f)["data"]
            self.anidb_anilist_mapping = {}
            titles_buckets = {}
            for anime in anime_list:
                anidb_url = None
                anilist_url = None
                for source in anime["sources"]:
                    if "anidb" in source:
                        anidb_url = source
                    if "anilist" in source:
                        anilist_url = source
                    if anidb_url and anilist_url:
                        continue
                if not anidb_url or not anilist_url:
                    if anidb_url or anilist_url:
                        for title in [anime["title"]] + anime["synonyms"]:
                            if title not in titles_buckets:
                                titles_buckets[title] = []
                            titles_buckets[title].append(anime)
                    continue
                self.anidb_anilist_mapping[
                    anidb_url[anidb_url.rindex("/") + 1 :]
                ] = anilist_url[anilist_url.rindex("/") + 1 :]
            len_matched = len(self.anidb_anilist_mapping)
            LOGGER.info("Found %s matching anidb and anilist entries.", len_matched)
            LOGGER.info(
                "Trying to match %s failed entries by title", len(titles_buckets)
            )
            for anime_sharing_title in titles_buckets.values():
                anidb_url = None
                anilist_url = None
                if (
                    len(anime_sharing_title) != 2
                    or anime_sharing_title[0]["animeSeason"]["season"]
                    != anime_sharing_title[1]["animeSeason"]["season"]
                    or anime_sharing_title[0]["animeSeason"]["year"]
                    != anime_sharing_title[1]["animeSeason"]["year"]
                    or anime_sharing_title[0]["episodes"]
                    != anime_sharing_title[1]["episodes"]
                ):
                    continue
                for source in (
                    anime_sharing_title[0]["sources"]
                    + anime_sharing_title[1]["sources"]
                ):
                    if "anidb" in source:
                        anidb_url = source
                    if "anilist" in source:
                        anilist_url = source
                    if anidb_url and anilist_url:
                        continue
                if not anidb_url or not anilist_url:
                    continue
                self.anidb_anilist_mapping[
                    anidb_url[anidb_url.rindex("/") + 1 :]
                ] = anilist_url[anilist_url.rindex("/") + 1 :]
            LOGGER.info(
                "Matched by title: %s", len(self.anidb_anilist_mapping) - len_matched
            )

    def get_tvdb_anidb_mapping(self):
        p = pathlib.Path(TVDB_ANIDB_ANIME_LIST_FILE)
        self.download_file(TVDB_ANIDB_ANIME_LIST_URL, TVDB_ANIDB_ANIME_LIST_FILE)
        with p.open("rb") as f:
            self.tvdb_anidb_mapping = {}
            repeated_ids = set()
            parser = etree.XMLParser()
            root = etree.parse(f, parser)
            for el in root.iterfind("anime"):
                if el.get("tvdbid") in self.tvdb_anidb_mapping:
                    repeated_ids.add(el.get("tvdbid"))
                self.tvdb_anidb_mapping[el.get("tvdbid")] = el.get("anidbid")
            LOGGER.error(
                "TVDB ids are shared by multiple anidb entries. Removing: %s",
                repeated_ids,
            )
            for rl in repeated_ids:
                self.tvdb_anidb_mapping.pop(rl)

    def download_file(self, url, filename):
        with requests.get(
            url,
            stream=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
            },
        ) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
