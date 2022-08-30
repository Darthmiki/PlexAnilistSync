import logging

from PlexAnimeHelper import PlexAnimeHelper
from AnilistHelper import AnilistHelper

LOGGER = logging.getLogger(__name__)


class PlexAnilistSync:
    def __init__(
        self,
        plex_anilist_matcher,
        anilist_token,
        anilist_username,
        plex_username,
        plex_password,
        plex_server_dict,
    ):
        try:
            self.anilist_helper = AnilistHelper(anilist_username, anilist_token)
            self.anilist_user = anilist_username
            self.plex_anime_helper = PlexAnimeHelper(
                plex_username,
                plex_password,
                plex_server_dict,
            )
            self.plex_anilist_matcher = plex_anilist_matcher
            self.plex_server_dict = plex_server_dict
            self.ok = True
        except Exception as exception:
            LOGGER.error("Could not initiate PlexAnilistSync: %s", exception)
            self.ok = False

    def sync(self):
        try:
            anilist_list = self.anilist_helper.get_user_list(self.anilist_user)
            if not anilist_list:
                LOGGER.warn("Could not get anilist")
                return
            LOGGER.info(
                "Found %s anime entries in %s anilist",
                len(anilist_list),
                self.anilist_user,
            )
            plex_watched_list = []
            for server in self.plex_server_dict.keys():
                for section in self.plex_server_dict[server]:
                    plex_watched_list.extend(
                        self.plex_anime_helper.get_shows_with_watched_episodes(
                            server, section
                        )
                    )
            LOGGER.info("Found %s anime with watched episodes", len(plex_watched_list))
            for plex_anime_entry in plex_watched_list:
                anilistId = self.plex_anilist_matcher.map_plex_guid_to_anilist_id(
                    plex_anime_entry.guid
                )
                LOGGER.info(
                    "-----------------------------------------------------------------"
                )
                if anilistId:
                    anilist_entry = anilist_list.get(anilistId)
                    if anilist_entry:
                        LOGGER.info(
                            "Anime %s - %s found in %s Anilist:",
                            anilistId,
                            anilist_entry["media"]["title"]["romaji"],
                            self.anilist_user,
                        )
                        if anilist_entry["status"] == "COMPLETED":
                            LOGGER.info("Anime is already completed. Skipping")
                            continue
                        plex_watched_episodes = (
                            self.plex_anime_helper.get_watched_episodes(
                                plex_anime_entry
                            )
                        )
                        if plex_watched_episodes == 0:
                            LOGGER.info("Only specials watched. Skipping")
                            continue
                        if plex_watched_episodes > anilist_entry["progress"]:
                            if (
                                anilist_entry["media"]["episodes"]
                                and plex_watched_episodes
                                >= anilist_entry["media"]["episodes"]
                                and anilist_entry["media"]["status"] == "FINISHED"
                            ):
                                LOGGER.info(
                                    "Updating %s - %s. New status: COMPLETED",
                                    anilistId,
                                    anilist_entry["media"]["title"]["romaji"],
                                )
                                self.anilist_helper.update_user_anilist_entry(
                                    anilistId,
                                    min(
                                        anilist_entry["media"]["episodes"],
                                        plex_watched_episodes,
                                    ),
                                    "COMPLETED",
                                )
                            else:
                                if anilist_entry["status"] == "PLANNING":
                                    LOGGER.info(
                                        "Updating %s - %s. New status: CURRENT %s/%s",
                                        anilistId,
                                        anilist_entry["media"]["title"]["romaji"],
                                        plex_watched_episodes,
                                        anilist_entry["media"]["episodes"]
                                        if "episodes" in anilist_entry["media"]
                                        else "?",
                                    )
                                    self.anilist_helper.update_user_anilist_entry(
                                        anilistId, plex_watched_episodes, "CURRENT"
                                    )
                                else:
                                    LOGGER.info(
                                        "Updating %s - %s. Keeping old status: %s",
                                        anilistId,
                                        anilist_entry["media"]["title"]["romaji"],
                                        anilist_entry["status"],
                                    )
                                    self.anilist_helper.update_user_anilist_entry(
                                        anilistId,
                                        plex_watched_episodes,
                                        anilist_entry["status"],
                                    )
                        else:
                            LOGGER.info("Same progress on Anilist and Plex. Skipping")

                    else:
                        LOGGER.warning(
                            "Anime with id: %s not in list. Looking for it", anilistId
                        )
                        anilist_media_entry = self.anilist_helper.get_by_id(anilistId)
                        if anilist_media_entry:
                            LOGGER.info(
                                "Found anime: %s",
                                anilist_media_entry["title"]["romaji"],
                            )
                            plex_watched_episodes = (
                                self.plex_anime_helper.get_watched_episodes(
                                    plex_anime_entry
                                )
                            )
                            if plex_watched_episodes == 0:
                                LOGGER.info("Only specials watched. Skipping")
                                continue
                            if (
                                anilist_media_entry["episodes"]
                                and plex_watched_episodes
                                >= anilist_media_entry["episodes"]
                                and anilist_media_entry["status"] == "FINISHED"
                            ):
                                LOGGER.info(
                                    "Updating %s - %s. New status: COMPLETED",
                                    anilistId,
                                    anilist_media_entry["title"]["romaji"],
                                )
                                self.anilist_helper.update_user_anilist_entry(
                                    anilistId,
                                    min(
                                        anilist_media_entry["episodes"],
                                        plex_watched_episodes,
                                    ),
                                    "COMPLETED",
                                )
                            else:
                                LOGGER.info(
                                    "Updating %s - %s. New status: CURRENT %s/%s",
                                    anilistId,
                                    anilist_media_entry["title"]["romaji"],
                                    plex_watched_episodes,
                                    anilist_media_entry["episodes"]
                                    if "episodes" in anilist_media_entry
                                    else "?",
                                )
                                self.anilist_helper.update_user_anilist_entry(
                                    anilistId, plex_watched_episodes, "CURRENT"
                                )

                        else:
                            LOGGER.warning("Anime %s not found", anilistId)
                else:
                    LOGGER.warning(
                        "Could not match id from Plex guid with anilist id: %s: %s",
                        plex_anime_entry.title,
                        plex_anime_entry.guid,
                    )
            LOGGER.info("Synchronization for %s finished", self.anilist_user)
        except Exception as exception:
            LOGGER.error("Synchronization failed: %s", exception)
