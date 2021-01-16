import simplejson as json

import time
import requests
import logging

LOGGER = logging.getLogger(__name__)


class AnilistHelper:
    def __init__(self, username, token):
        self.anilist_access_token = token
        self.username = username

    def _fetch_user_list(self):
        query = """
        query ($username: String) {
            MediaListCollection(userName: $username, type: ANIME) {
                lists {
                    name
                    status
                    isCustomList
                    entries {
                        id
                        progress
                        status
                        repeat
                        media {
                            id
                            type
                            format
                            status
                            source
                            season
                            episodes
                            startDate {
                                year
                                month
                                day
                            }
                            endDate {
                                year
                                month
                                day
                            }
                            title {
                                romaji
                                english
                                native
                            }
                            synonyms
                        }
                    }
                }
            }
        }
        """

        variables = {"username": self.username}

        url = "https://graphql.anilist.co"

        headers = {
            "Authorization": "Bearer " + self.anilist_access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = requests.post(
            url, headers=headers, json={"query": query, "variables": variables}
        )
        return json.loads(response.content)

    def _search_by_id(self, anilist_id):
        query = """
        query ($id: Int) {
          # Define which variables will be used in the query (id)
          media: Media (id: $id, type: ANIME) {
            # Insert our variables into the query arguments
            # (id) (type: ANIME is hard-coded in the query)
            id
            type
            format
            status
            source
            season
            episodes
            title {
                romaji
                english
                native
            }
            synonyms
            startDate {
                year
                month
                day
            }
            endDate {
                year
                month
                day
            }
          }
        }
        """

        variables = {"id": anilist_id}

        url = "https://graphql.anilist.co"

        headers = {
            "Authorization": "Bearer " + self.anilist_access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = requests.post(
            url, headers=headers, json={"query": query, "variables": variables}
        )
        return json.loads(response.content)

    def _update_series(self, mediaId, progress, status):
        query = """
        mutation ($mediaId: Int, $status: MediaListStatus, $progress: Int) {
            SaveMediaListEntry (mediaId: $mediaId, status: $status, progress: $progress) {
                id
                status,
                progress
            }
        }
        """

        variables = {"mediaId": mediaId, "status": status, "progress": int(progress)}

        url = "https://graphql.anilist.co"

        headers = {
            "Authorization": "Bearer " + self.anilist_access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        requests.post(url, headers=headers, json={"query": query, "variables": variables})

    def get_user_list(self):
        user_list_data = self._fetch_user_list()
        all_user_anime = {}
        try:
            if not user_list_data:
                LOGGER.warning("Could not get user list from Anilist")
                return None

            for sub_list in user_list_data["data"]["MediaListCollection"]["lists"]:
                for anime in sub_list["entries"]:
                    all_user_anime[str(anime["media"]["id"])] = anime
            time.sleep(.5)
            return all_user_anime
        except Exception as exception:
            LOGGER.error("Could not get user list from Anilist: %s", exception)
            return None

    def get_by_id(self, anilist_id):
        try:
            anilist_anime = self._search_by_id(anilist_id)
            if "data" in anilist_anime and "media" in anilist_anime["data"]:
                time.sleep(.5)
                return anilist_anime["data"]["media"]
            return None
        except Exception as exception:
            LOGGER.error("Could not get Anime from Anilist: %s", exception)
            return None

    def update_user_anilist_entry(self, mediaId, progress, status):
        try:
            self._update_series(mediaId, progress, status)
            time.sleep(.5)
        except Exception as exception:
            LOGGER.error("Could not update %s list: %s", self.username, exception)
