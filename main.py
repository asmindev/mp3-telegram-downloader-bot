from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from flask import Flask, request
from flask_cors import CORS, cross_origin
from yt import Youtube
from unduh import Main
import requests
import telepot
import re
import os

app = Flask(__name__)
CORS(app)

bot = telepot.Bot("1468139592:AAFoNdHFTpOWWeYQAyT4yAWbQ3Y6mPb-j_0")


class Downloader:
    def __init__(self):
        self.__position = []
        self._bot = None
        self._song = Main()
        self.__MESSAGES_NOW = []
        self.__AFTER_DOWNLOAD = []

    def download(self, uid, query, judul, tipe=None, ytlink=False, delete=None):
        judul = judul + ".mp3"
        stts = dict()
        if tipe is not None:
            if tipe == "joox":
                stts = self._song.joox_get_source(query, judul)
            if tipe == "dl":
                stts = self._song.get_source(query, judul, ytlink=ytlink)
        else:
            stts = self._song.get_source(query, judul, ytlink=ytlink)
        if delete:
            for index, item in enumerate(delete):
                if uid == item["uid"]:
                    del_msg = telepot.message_identifier(item["identifier"])
                    bot.deleteMessage(del_msg)
                    delete.pop(index)
        if stts.get("success"):
            bot.sendAudio(uid, open(judul, "rb"), title=stts.get("judul"))
        else:
            bot.sendMessage(uid, stts.get("msg"), parse_mode="Markdown")

    def inline_markup(self, new_msg):
        "Handling message Markup"
        uid = new_msg["message"]["chat"]["id"]
        id = eval(new_msg["data"])["id"]
        tipe = eval(new_msg["data"])["tipe"]
        for count, msg in enumerate(self.__MESSAGES_NOW):
            if msg["uid"] == uid:
                self.__MESSAGES_NOW.pop(count)  # Delete element if user reply
                delete = msg["identifier"]
                data = new_msg["message"]["reply_markup"]["inline_keyboard"]
                for item in data:
                    call_id = eval(item[0]["callback_data"])["id"]
                    if call_id == id:
                        judul = item[0]["text"]
                        ident = telepot.message_identifier(delete)
                        bot.editMessageReplyMarkup(ident, reply_markup=None)
                        pesan = "Downloading *%s*" % judul
                        down = bot.editMessageText(
                            ident, pesan, parse_mode="Markdown")
                        self.__AFTER_DOWNLOAD.append(
                            dict(uid=uid, identifier=down))
                        self.download(
                            uid,
                            id,
                            judul,
                            tipe=tipe,
                            delete=self.__AFTER_DOWNLOAD,
                        )
        return

    def _received_msg(self, new_msg):
        uid = new_msg["message"]["chat"]["id"]
        pesan = new_msg["message"].get("text")
        if pesan:
            for count, msg in enumerate(self.__MESSAGES_NOW):
                if msg["uid"] == uid:
                    # Delete element if user reply
                    self.__MESSAGES_NOW.pop(count)
                    delete = msg["identifier"]
                    ident = telepot.message_identifier(delete)
                    bot.deleteMessage(ident)
            if str(uid) in str(self.__position):
                for index, element in enumerate(self.__position):
                    if uid == element["uid"]:
                        if element["position"] == "dl":
                            tipe = "dl"
                            self.__position.pop(index)
                        if element["position"] == "joox":
                            tipe = "joox"
                            self.__position.pop(index)
                        if element["position"] == "yt":
                            self.__position.pop(index)
                            try:
                                a = requests.get(pesan).text
                                judul = re.findall("<title>(.*?)</title>", a)[
                                    0
                                ].replace(" - YouTube", "")
                                judul = "_".join(
                                    [i for i in re.findall(
                                        "\w*", judul) if i != ""]
                                )
                                return self.download(uid, pesan, judul, ytlink=True)
                            except Exception as err:
                                print(err)
                                return err
                self._select_song(uid, pesan, tipe)
            else:

                if pesan.startswith("/dl"):
                    query = pesan.split(" ", maxsplit=1)
                    if len(query) == 1:
                        markup = ForceReply(selective=False)
                        pesan = "Ok, berikan saya query lagu yang mau dicari"
                        bot.sendMessage(uid, pesan, reply_markup=markup)
                        self.__position.append(dict(uid=uid, position="dl"))
                    else:
                        self._select_song(uid, query[1], "dl")
                elif pesan.startswith("/yt"):
                    url = pesan.split(" ", maxsplit=1)
                    if len(url) == 1:
                        markup = ForceReply(selective=False)
                        pesan = "Ok, berikan saya link youtubenya"
                        bot.sendMessage(uid, pesan, reply_markup=markup)
                        self.__position.append(dict(uid=uid, position="yt"))
                    else:
                        try:
                            a = requests.get(url[1]).text
                            judul = re.findall("<title>(.*?)</title>", a)[0].replace(
                                " - YouTube", ""
                            )
                            judul = "_".join(
                                [i for i in re.findall(
                                    "\w*", judul) if i != ""]
                            )
                            self.download(
                                uid, url[1], judul=judul, ytlink=True)
                        except Exception as err:
                            print(err)
                            return err

                elif pesan.startswith("/joox"):
                    query = pesan.split(" ", maxsplit=1)
                    if len(query) == 1:
                        markup = ForceReply(selective=False)
                        pesan = "Ok, berikan saya query yang mau dicari"
                        bot.sendMessage(uid, pesan, reply_markup=markup)
                        self.__position.append(dict(uid=uid, position="joox"))
                    else:
                        self._select_song(uid, query[1], "joox")
                elif pesan.startswith("/start"):
                    pesan = "Penggunaan\n"
                    pesan += "/dl [query]\n"
                    pesan += "Contoh:\n"
                    pesan += "      /dl Noah\n\n"
                    pesan += "/yt [url]\n"
                    pesan += "Contoh:\n\t"
                    pesan += "      /yt https://youtu.be/y6e_kztXG04"
                    bot.sendMessage(uid, pesan, disable_web_page_preview=True)
                else:
                    pesan = "Pesan tidak dikenali\n"
                    pesan += "/dl [query]\n"
                    pesan += "Contoh:\n"
                    pesan += "      /dl Noah\n\n"
                    pesan += "/yt [url]\n"
                    pesan += "Contoh:\n\t"
                    pesan += "      /yt https://youtu.be/y6e_kztXG04"
                    bot.sendMessage(uid, pesan, disable_web_page_preview=True)
        else:
            bot.sendMessage(uid, "Bot hanya mengenali pesan yang berupa text ")

    def _select_song(self, uid, query, tipe):
        arr = []
        if tipe == "joox":
            results = self._song.joox_search(query)
        else:
            results = self._song.youtube_search(query)
        if results.get("status"):
            for item in results.get("songs"):
                arr.append(
                    [
                        InlineKeyboardButton(
                            text=item["judul"],
                            callback_data=str(
                                dict(id=item.get("id"), tipe=tipe)),
                        )
                    ]
                )
            markup = InlineKeyboardMarkup(inline_keyboard=arr)
            for count, cek in enumerate(self.__MESSAGES_NOW):
                if cek["uid"] == uid:
                    del_msg = telepot.message_identifier(cek["identifier"])
                    bot.deleteMessage(del_msg)
                    self.__MESSAGES_NOW.pop(count)
            text = bot.sendMessage(uid, "Select song", reply_markup=markup)
            data = {"uid": uid, "identifier": text}
            self.__MESSAGES_NOW.append(data)
        else:
            pesan = "Query *%s* tidak ditemukan" % query
            bot.sendMessage(uid, pesan, parse_mode="Markdown")
        return "ok"


mp = Downloader()


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        new_msg = request.get_json()
        if "message" in str(new_msg):
            if new_msg.get("message"):
                mp._received_msg(new_msg)
            else:
                if new_msg.get("callback_query"):
                    mp.inline_markup(new_msg["callback_query"])
        return "ok"
    else:
        return "Ok"


@cross_origin
@app.route("/api/youtube")
def api():
    arg = request.args
    link = arg.get("link")
    if link:
        yt = Youtube()
        result = yt.metadata(link)
        return result
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(
        os.environ.get("PORT", "5000")), debug=True)
