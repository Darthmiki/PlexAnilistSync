import logging
import os
import sys
import coloredlogs
import time

from PlexAnilistMatcher import PlexAnilistMatcher
from PlexAnilistSync import PlexAnilistSync

LOGGER = logging.getLogger(__name__)

logging.basicConfig(
    level=20,
    format="%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s",
)
coloredlogs.install(level="DEBUG")

INTERVAL = int(os.getenv("LIST_UPDATE_INTERVAL", 3600))
ANILIST_TOKEN = os.getenv("ANILIST_TOKEN", "")
ANILIST_USERNAME = os.getenv("ANILIST_USERNAME", "")
PLEX_USERNAME = os.getenv("PLEX_USERNAME", "")
PLEX_PASSWORD = os.getenv("PLEX_PASSWORD", "")
PLEX_SERVER_NAME = os.getenv("PLEX_SERVER_NAME", "")
PLEX_SECTION_NAME = os.getenv("PLEX_SECTION_NAME", "")


def main():
    if (
        not ANILIST_TOKEN
        or not ANILIST_USERNAME
        or not PLEX_USERNAME
        or not PLEX_PASSWORD
        or not PLEX_SERVER_NAME
        or not PLEX_SECTION_NAME
    ):
        sys.exit("Missing environment variables")
    matcher = PlexAnilistMatcher()
    plex_anilist_sync = PlexAnilistSync(
        matcher,
        ANILIST_TOKEN,
        ANILIST_USERNAME,
        PLEX_USERNAME,
        PLEX_PASSWORD,
        {PLEX_SERVER_NAME: [PLEX_SECTION_NAME]},
    )
    while True:
        plex_anilist_sync.sync()
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
