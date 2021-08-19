import requests
from bs4 import BeautifulSoup
from typing import Text


class Youtube:
    def __init__(self) -> None:
        self.link = "https://x2convert.com/ajax2/getFile.ashx?linkinfo="

    def metadata(self, link: Text):
        response = requests.get(self.link + link)
        if response.status_code == 200 and response.json()["Message"].startswith(
            "http"
        ):
            data = response.json()
            print(data)
            text = requests.get(data["Message"]).text
            to_bs4 = BeautifulSoup(text, "html.parser")
            link = to_bs4.find("a", {"class": "btn-success"})
            thumbnail = to_bs4.find(
                "img", {"class": "img-thumbnail"}).get("src")
            return dict(
                url=link.get("href"),
                thumbnail=thumbnail,
                judul=data.get("Name"),
                size=data.get("Size"),
                msg="sucess get file",
            )
        else:
            return dict(msg="failed get file")
