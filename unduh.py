import requests
import eyed3


class Main:
    def __init__(self):
        self.__url = "https://www.downloadlagu321.net"
        self.__joox = "https://public-restapi.herokuapp.com/api/joox/"

    def joox_search(self, query):
        songs = []
        params = {"q": query}
        list_song = (
            requests.get(self.__joox + "search/",
                         params=params).json().get("songs")
        )
        if len(list_song) != 0:
            for song in list_song:
                title = song["singerName"] + " - " + song["title"]
                id = song["id"]
                songs.append(dict(judul=title, id=id))
            return dict(status=True, songs=songs)
        else:
            return dict(status=False, songs=songs)

    def joox_get_source(self, uid, filename):
        params = {"id": uid}
        res = requests.get(self.__joox + "show/", params=params).json()[0]
        mp3_link = res["downloadLinks"]["mp3"]
        get_size = requests.get(mp3_link, stream=True)
        size = get_size.headers.get("Content-Length")
        title = res["singerName"] + " - " + res["songName"]
        with open(title + ".jpg", "wb") as f:
            tmb = requests.get(res["thumbNail"]).content
            f.write(tmb)
        if 7200000 >= int(size):
            with open(filename, "wb") as f:
                response = requests.get(mp3_link).content
                f.write(response)
            _edit = eyed3.load(filename)
            _edit.tag.title = title
            _edit.tag.artist = res["singerName"]
            _edit.tag.album = "Xiuz Downloader"
            _edit.tag.images.set(
                3, open(title + ".jpg", "rb").read(), "image/jpeg")
            _edit.tag.save()
            return dict(success=True, judul=title, msg="sukses bro!!")
        else:
            return dict(
                success=False,
                judul=None,
                msg="Ukuran *%s* Kebesaran. Minimal 7 Mb" % title,
            )

    def youtube_search(self, query):
        array = []
        data = requests.get(
            self.__url + "/api/search/%s" % query.replace(" ", "%20"), verify=False
        )
        try:
            data = data.json()
            if len(data) != 0:
                for item in data:
                    judul = item.get("title")
                    id = item.get("id")
                    array.append(dict(judul=judul, id=id))
                return dict(status=True, songs=array)
            else:
                return dict(status=False, songs=array)
        except Exception:
            return dict(status=False, songs=array)

    def get_source(self, raw_link, filename, ytlink=False):
        # url = "https://michaelbelgium.me/ytconverter/convert.php?youtubelink=https://www.youtube.com/watch?v="
        if ytlink:
            new = "https://nuubi.herokuapp.com/api/y2mate/download/mp3?url=%s&quality=128"

        else:
            new = "https://nuubi.herokuapp.com/api/y2mate/download/mp3?url=https://www.youtube.com/watch?v=%s&quality=128"
        url = requests.get(new % raw_link).json()

        if url.get("url"):
            get_size = requests.get(url.get("url"), stream=True)
            size = get_size.headers.get("Content-Length")
            thumb = filename.split(".")[0] + ".jpg"
            if size:
                if 7200000 >= int(size):
                    with open(filename, "wb") as f:
                        response = requests.get(url.get("url"))
                        f.write(response.content)
                    with open(thumb, "wb") as f:
                        f.write(requests.get(url.get("thumbnail")).content)
                    audio = eyed3.load(filename)
                    audio.tag.title = url.get("judul").replace(".mp3", "")
                    audio.tag.artist = "Xiuz"
                    audio.tag.album = "Xiuz Downloader"
                    audio.tag.images.set(
                        3,
                        open(thumb, "rb").read(),
                        "image/jpeg",
                    )
                    audio.tag.save()
                    return dict(
                        success=True, judul=url.get("judul"), msg="sukses bro!!"
                    )
                else:
                    return dict(
                        success=False,
                        judul=None,
                        msg="Ukuran *%s* Kebesaran. Minimal 7 Mb" % url.get(
                            "judul"),
                    )
        else:
            return dict(success=False, judul=None, msg=url.get("error"))


# c = Main()
# c.youtube_search('https://youtu.be/Id6jNuZFX7k')
# c.get_source("6oi5_UyUnds", "asu.mp3")
