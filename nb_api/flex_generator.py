from line_magic.line_magic.message import FlexMessage
from copy import deepcopy
import json
import os


class NuxtImageBoardFlexGenerator(object):
    def __init__(self, dir="flex", cdn_endpoint="https://example.com"):
        flex = {}
        for file in os.listdir(dir):
            with open(os.path.join(dir, file), "r", encoding="utf-8") as f:
                data = json.loads(f.read())
            flex[file[:-5]] = data
        self.flex = flex
        self.cdn_endpoint = cdn_endpoint

    def generateImageSearchResultCarousel(self, search_result):
        contents = []
        for d in search_result["data"]["result"]:
            result = deepcopy(self.flex["image_search_result"])
            result["action"]["uri"] = d["urls"]["source"]
            result["body"]["contents"][0]["url"] = f"https://ascii2d.net{d['thumbnail']}"
            result["body"]["contents"][1]["contents"][0]["text"] = d["size"]
            result["body"]["contents"][2]["contents"][0]["text"] = d["artist"]
            result["body"]["contents"][3]["contents"][0]["text"] = "Pixiv" if "pixiv" in d["urls"]["source"] else "Twitter"
            result["footer"]["contents"][0]["contents"][0]["text"] = d["title"]
            contents.append(result)
        return FlexMessage({"type": "carousel", "contents": contents})

    def generateNormalSearchResultCarousel(self, search_result):
        search_result["data"]["imgs"] = [r for r in search_result["data"]["imgs"] if r["nsfw"] == 0]
        contents = []
        for d in search_result["data"]["imgs"][:9]:
            result = deepcopy(self.flex["search_result"])
            result["action"]["uri"] = d["originUrl"]
            result["body"]["contents"][0]["url"] = f"https://{self.cdn_endpoint}/illusts/thumb/{d['illustID']}.jpg"
            result["body"]["contents"][1]["contents"][0]["text"] = d["artist"]["name"]
            result["body"]["contents"][2]["contents"][0]["text"] = d["date"].split(" ")[0]
            result["body"]["contents"][3]["contents"][0]["text"] = d["originService"]
            result["footer"]["contents"][0]["contents"][0]["text"] = d["title"]
            contents.append(result)
        return FlexMessage({"type": "carousel", "contents": contents})

    def generateTagSearchCarousel(self, search_result, title):
        contents = []
        for d in search_result["data"]["contents"][:10]:
            result = deepcopy(self.flex["search_tag"])
            result["action"]["text"] = f"{title} {d['id']}"
            result["body"]["contents"][1]["text"] = f"該当数: {d['count']}"
            result["body"]["contents"][2]["text"] = f"いいね数: {d['lcount']}"
            result["footer"]["contents"][0]["contents"][0]["text"] = d["name"]
            contents.append(result)
        return FlexMessage({"type": "carousel", "contents": contents})
