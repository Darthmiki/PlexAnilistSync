import logging
import time

from PlexAnilistMatcher import PlexAnilistMatcher
from PlexAnilistSync import PlexAnilistSync

LOGGER = logging.getLogger(__name__)


class BatchSyncWorker():
    def __init__(self, config):
        self.matcher = PlexAnilistMatcher()
        self.interval = config["interval_in_seconds"] if "interval_in_seconds" in config else 3600
        if "config" not in config:
            raise ValueError("config missing in config")
        self.plex_anilist_sync_jobs = []
        for conf in config["config"]:
            plex_anilist_sync = PlexAnilistSync(self.matcher, conf)
            if plex_anilist_sync.ok:
                self.plex_anilist_sync_jobs.append(plex_anilist_sync)
    
    def run_periodic_sync_jobs(self):
        while True:
            for job in self.plex_anilist_sync_jobs:
                time.sleep(5)
                job.sync()
            time.sleep(self.interval)
                
            

