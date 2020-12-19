import requests


class NuxtImageBoardClient():
    def __init__(self, token, endpoint):
        self.endpoint = endpoint
        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    def getRankings(self):
        return requests.get(
            f"{self.endpoint}/ranking/monthly/likes",
            headers=self.headers
        ).json()

    def getRecents(self, page=1, sort="d", order="d"):
        return requests.get(
            f"{self.endpoint}/search/all",
            params={"page": page, "sort": sort, "order": order},
            headers=self.headers
        ).json()

    def getTagList(self, page=1, sort="c", order="d"):
        return requests.get(
            f"{self.endpoint}/catalog/tags",
            params={"page": page, "sort": sort, "order": order},
            headers=self.headers
        ).json()

    def getCharacterList(self, page=1, sort="c", order="d"):
        return requests.get(
            f"{self.endpoint}/catalog/characters",
            params={"page": page, "sort": sort, "order": order},
            headers=self.headers
        ).json()

    def getArtistList(self, page=1, sort="c", order="d"):
        return requests.get(
            f"{self.endpoint}/catalog/artists",
            params={"page": page, "sort": sort, "order": order},
            headers=self.headers
        ).json()

    def searchWithTag(self, id, page=1, sort="d", order="d"):
        return requests.get(
            f"{self.endpoint}/search/tag",
            params={"id": id, "page": page, "sort": sort, "order": order},
            headers=self.headers
        ).json()

    def searchOnAscii2d(self, filename, contentType="image/jpeg"):
        with open(filename, "rb") as f:
            return requests.post(
                f"{self.endpoint}/search/image/ascii2d",
                files={
                    "file": (filename.split("/")[-1], f.read(), contentType)
                },
                headers=self.headers
            ).json()
