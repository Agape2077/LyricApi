from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
import netease
import qqmusic

app = Flask(__name__)


def fetch_netease_data(song_id):
    """
    为单个网易云歌曲ID获取艺术家、标题和歌词。
    这是一个辅助函数，用于在线程池中执行。
    """
    try:
        song_artist, song_title = netease.getInfo(song_id)
        lyrics = netease.getLyric(song_id)
        return {
            "source": "Netease",
            "id": str(song_id),
            "title": song_title,
            "artist": song_artist,
            "lyrics": lyrics
        }
    except Exception as e:
        print(f"无法处理网易云歌曲ID {song_id}: {e}")
        return None


def fetch_qqmusic_data(song_info):
    """
    为单个QQ音乐歌曲信息获取歌词。
    这是一个辅助函数，用于在线程池中执行。
    """
    try:
        lyrics = qqmusic.getLyric(song_info['songid'], song_info['songmid'])
        return {
            "source": "QQMusic",
            "id": str(song_info['songid']),
            "title": song_info['title'],
            "artist": song_info['artist'],
            "lyrics": lyrics
        }
    except Exception as e:
        print(f"无法处理QQ音乐歌曲ID {song_info['songid']}: {e}")
        return None


@app.route("/lyric", methods=['GET'])
def get_data():
    """
    此接口用于聚合搜索歌词。
    接收 'artist' 和 'title' 作为查询参数。
    使用多线程并发从网易云和QQ音乐获取最多各3首匹配歌曲的信息。
    """
    try:
        artist = str(request.args.get('artist', ''))
        title = str(request.args.get('title', ''))

        if not title:
            return jsonify({"error": "必须提供 'title' 参数。"}), 400

        # 分别从两个平台搜索
        netease_song_ids = netease.search(title, artist)
        qq_songs_info = qqmusic.search(title, artist)

        all_results = []
        # 使用ThreadPoolExecutor并发获取所有歌曲数据
        with ThreadPoolExecutor(max_workers=6) as executor:
            # 提交网易云音乐的任务
            netease_futures = executor.map(fetch_netease_data, netease_song_ids[:3])
            # 提交QQ音乐的任务
            qqmusic_futures = executor.map(fetch_qqmusic_data, qq_songs_info[:3])

            # 收集结果，并过滤掉失败的项 (None)
            netease_results = [res for res in netease_futures if res is not None]
            qqmusic_results = [res for res in qqmusic_futures if res is not None]

            all_results.extend(netease_results)
            all_results.extend(qqmusic_results)

        return jsonify(all_results)

    except Exception as e:
        print(f"发生严重错误: {e}")
        return jsonify({"error": "服务器内部错误，请稍后再试。"}), 500


@app.route("/")
def index():
    """
    服务主页。
    """
    return """
    <html>
    <head>
        <title>聚合歌词搜索 API</title>
        <style>
            body { font-family: sans-serif; line-height: 1.6; padding: 2em; }
            h1 { color: #333; }
            p { color: #555; }
            code { background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>聚合歌词搜索 API</h1>
        <p>这是一个聚合歌词服务器。请使用 <code>/lyric</code> 接口来获取歌词。</p>
        <p>使用示例: <code>/lyric?title=歌曲名&artist=艺术家名</code></p>
        <p>返回结果会包含一个 <code>source</code> 字段来区分来源 (<code>Netease</code> 或 <code>QQMusic</code>)。</p>
    </body>
    </html>
    """


if __name__ == '__main__':
    from waitress import serve

    serve(app, port=10492, host="0.0.0.0")