from flask import Flask, request
from line_magic.line_magic import (
    LineMessagingClient, LineMessagingTracer,
    TextMessage, FlexMessage,
    TraceType
)
from nb_api.flex_generator import NuxtImageBoardFlexGenerator
from nb_api.client import NuxtImageBoardClient
from dotenv import load_dotenv
from nudenet import NudeClassifierLite
from copy import deepcopy
import requests
import tempfile
import os

# .env読み出し
load_dotenv(verbose=True, override=True)

# 各種クライアントの作成
classifier = NudeClassifierLite()
cl = LineMessagingClient(
    channelAccessToken=os.environ.get("LINE_CHANNEL_TOKEN")
)
tracer = LineMessagingTracer(cl, None, ["!", "?", "#", "."])
igl = NuxtImageBoardFlexGenerator(
    "flex",
    os.environ.get("CDN_ENDPOINT")
)
icl = NuxtImageBoardClient(
    os.environ.get("API_TOKEN"),
    os.environ.get("API_ENDPOINT")
)


# イベント別受信処理
class Events(object):
    @tracer.Before(TraceType.EVENT)
    def set_Token(self, ctx, cl, op):
        if "replyToken" in op:
            cl.setReplyToken(op["replyToken"])

    @tracer.Event("message")
    def got_message(self, ctx, cl, msg):
        ctx.trace(msg, TraceType.CONTENT)

    @tracer.Event("follow")
    def got_follow(self, ctx, cl, op):
        msgs = [TextMessage("友達登録ありがとうございます!")]
        cl.replyMessage(msgs)


# コンテンツ別受信処理
class Contents(object):
    @tracer.Content("text")
    def got_text(self, ctx, cl, msg):
        ctx.trace(msg, TraceType.COMMAND)

    @tracer.Content("image")
    def got_image(self, ctx, cl, msg):
        with tempfile.TemporaryDirectory() as path:
            with open(f"{path}/img.jpg", "wb") as f:
                f.write(cl.getContent(msg["message"]["id"]))
            search_result = icl.searchOnAscii2d(f"{path}/img.jpg")
            new_result = []
            for r in search_result["data"]["result"]:
                # nsfwな結果は除外
                with open(f"{path}/check.jpg", "wb") as f:
                    f.write(requests.get(f"https://ascii2d.net{r['thumbnail']}").content)
                nsfw_result = classifier.classify(f"{path}/check.jpg")
                if nsfw_result[f"{path}/check.jpg"]["unsafe"] < 0.55:
                    new_result.append(r)
            search_result["data"]["result"] = new_result
        msgs = [igl.generateImageSearchResultCarousel(search_result)]
        cl.replyMessage(msgs)


# コマンド別受信処理
class Commands(object):
    @tracer.Command(alt=["ハロー", "hello"])
    def hi(self, ctx, cl, msg):
        '''Check the bot Alive'''
        msgs = [TextMessage("Hi too!")]
        cl.replyMessage(msgs)

    @tracer.Command(noPrefix=True)
    def help(self, ctx, cl, msg):
        '''Display this help message'''
        msgs = [TextMessage(ctx.genHelp())]
        cl.replyMessage(msgs)

    @tracer.Command(prefix=False)
    def イラスト検索(self, ctx, cl, msg):
        msgs = [FlexMessage(igl.flex["search_methods"])]
        cl.replyMessage(msgs)

    @tracer.Command(prefix=False)
    def タグから探す(self, ctx, cl, msg):
        tags = icl.getTagList()
        msgs = [igl.generateTagSearchCarousel(tags, title="タグ検索")]
        cl.replyMessage(msgs)

    @tracer.Command(prefix=False)
    def キャラクターから探す(self, ctx, cl, msg):
        tags = icl.getCharacterList()
        msgs = [igl.generateTagSearchCarousel(tags, title="キャラクター検索")]
        cl.replyMessage(msgs)

    @tracer.Command(prefix=False)
    def 絵師から探す(self, ctx, cl, msg):
        artists = icl.getArtistList()
        msgs = [igl.generateTagSearchCarousel(artists, title="絵師検索")]
        cl.replyMessage(msgs)

    @tracer.Command(prefix=False)
    def 画像から探す(self, ctx, cl, msg):
        msgs = [TextMessage("検索したい画像を送信または転送してください!\n(検索には10~15秒程度かかります)")]
        cl.replyMessage(msgs)

    @tracer.Command(prefix=False)
    def ランキング検索(self, ctx, cl, msg):
        search_result = icl.getRankings()
        msgs = [igl.generateNormalSearchResultCarousel(search_result)]
        cl.replyMessage(msgs)

    @tracer.Command(prefix=False, inpart=True)
    def 新着イラスト(self, ctx, cl, msg):
        args = ctx.getArg(["新着イラスト"], msg["message"]["text"], ignoreCase=False)
        if not args:
            search_result = icl.getRecents()
        elif not args[0].isdigit():
            search_result = icl.getRecents()
        else:
            page = int(args[0])
            if page % 2 == 0:
                search_result = icl.getRecents(page=page - 1)
            else:
                search_result = icl.getRecents(page=page)
            if page % 2 == 0:
                search_result["data"]["imgs"] = search_result["data"]["imgs"][10:]
        msgs = [igl.generateNormalSearchResultCarousel(search_result)]
        cl.replyMessage(msgs)

    @tracer.Command(prefix=False, inpart=True)
    def タグ検索(self, ctx, cl, msg):
        args = ctx.getArg(["タグ検索"], msg["message"]["text"], ignoreCase=False)
        if not args:
            msgs = [TextMessage("タグIDを指定してください")]
            cl.replyMessage(msgs)
            return
        if not args[0].isdigit():
            msgs = [TextMessage("タグIDが正しくありません")]
            cl.replyMessage(msgs)
            return
        search_result = icl.searchWithTag(args[0])
        if not search_result:
            msgs = [TextMessage("タグIDが正しくないか、該当する結果がありませんでした")]
            cl.replyMessage(msgs)
            return
        msgs = [igl.generateNormalSearchResultCarousel(search_result)]
        cl.replyMessage(msgs)

    @tracer.Command(prefix=False, inpart=True)
    def キャラクター検索(self, ctx, cl, msg):
        args = ctx.getArg(["キャラクター検索"], msg["message"]["text"], ignoreCase=False)
        if not args:
            msgs = [TextMessage("キャラクターIDを指定してください")]
            cl.replyMessage(msgs)
            return
        if not args[0].isdigit():
            msgs = [TextMessage("キャラクターIDが正しくありません")]
            cl.replyMessage(msgs)
            return
        search_result = icl.searchWithTag(args[0])
        if not search_result:
            msgs = [TextMessage("キャラクターIDが正しくないか、該当する結果がありませんでした")]
            cl.replyMessage(msgs)
            return
        msgs = [igl.generateNormalSearchResultCarousel(search_result)]
        cl.replyMessage(msgs)

    @tracer.Command(prefix=False, inpart=True)
    def 絵師検索(self, ctx, cl, msg):
        args = ctx.getArg(["絵師検索"], msg["message"]["text"], ignoreCase=False)
        if not args:
            msgs = [TextMessage("絵師IDを指定してください")]
            cl.replyMessage(msgs)
            return
        if not args[0].isdigit():
            msgs = [TextMessage("絵師IDが正しくありません")]
            cl.replyMessage(msgs)
            return
        search_result = icl.searchWithTag(args[0])
        if not search_result:
            msgs = [TextMessage("絵師IDが正しくないか、該当する結果がありませんでした")]
            cl.replyMessage(msgs)
            return
        msgs = [igl.generateNormalSearchResultCarousel(search_result)]
        cl.replyMessage(msgs)


def app_callback():
    if request.method == "POST":
        data = request.get_json()
        for d in data["events"]:
            tracer.trace(d, TraceType.EVENT)
    return "OK"


def createApp():
    app = Flask(__name__)
    app.add_url_rule('/callback', 'callback', app_callback, methods=["GET", "POST"])
    tracer.addClass(Events())
    tracer.addClass(Contents())
    tracer.addClass(Commands())
    tracer.startup()
    return app

app = createApp()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1204)
