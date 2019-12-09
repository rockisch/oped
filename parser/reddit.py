import time
from datetime import datetime, timedelta

import requests


class Client:
    def __init__(self, auth_data: dict, user_agent: str):
        self.auth_data = auth_data
        self.user_agent = user_agent
        self._endpoint = "https://oauth.reddit.com"

        self._expire_in = 0
        self._last_auth = datetime.min

        self._wait = 0
        self._last_request = datetime.min

    @property
    def auth_key(self) -> str:
        if (datetime.now() - self._last_auth).seconds > self._expire_in - 1:
            r = requests.post(
                "https://www.reddit.com/api/v1/access_token",
                headers={"User-Agent": "OPED User Agent 0.1"},
                data=self.auth_data,
                auth=("bdJpF9eA5Vz4Dw", "B2SIAD6-nketU9gHusKx-y9cRWo"),
            )
            r.raise_for_status()

            data = r.json()
            self._auth_key = data["access_token"]
            self._expire_in = data["expires_in"]
            self._last_auth = datetime.now()

        return self._auth_key

    def request(self, method: str, url: str, data: dict = {}) -> dict:
        if self._wait and (datetime.now() - self._last_request).seconds < self._wait:
            time.sleep()

        headers = {
            "Authorization": f"bearer {self.auth_key}",
            "User-Agent": self.user_agent,
        }
        r = requests.request(method, self._endpoint + url, headers=headers, data=data)
        r.raise_for_status()

        self._last_request = datetime.now()
        if float(r.headers["X-Ratelimit-Remaining"]) == 0:
            self._wait = r.headers["X-Ratelimit-Reset"]

        return r.json()

    def wiki_pages(self, subreddit: str) -> list:
        return self.request("GET", f"/r/{subreddit}/wiki/pages")["data"]

    def wiki_page(self, subreddit: str, page: str) -> dict:
        return self.request("GET", f"/r/{subreddit}/wiki/{page}")["data"]
