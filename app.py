from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
import netease

app = Flask(__name__)


def fetch_song_data(song_id):
    """
    为单个歌曲ID获取艺术家、标题和歌词。
    这是一个辅助函数，用于在线程池中执行。
    """
    try:
        song_artist, song_title = netease.getInfo(song_id)
        lyrics = netease.getLyric(song_id)
        return {
            "id": str(song_id),
            "title": song_title,
            "artist": song_artist,
            "lyrics": lyrics
        }
    except Exception as e:
        # 如果处理某个歌曲时出错，打印错误并返回None
        print(f"无法处理歌曲ID {song_id}: {e}")
        return None


@app.route("/lyric", methods=['GET'])
def get_data():
    """
    此接口用于搜索歌词。
    接收 'artist' 和 'title' 作为查询参数。
    使用多线程并发获取最多3首匹配歌曲的信息并以JSON列表形式返回。
    """
    try:
        artist = str(request.args.get('artist', ''))
        title = str(request.args.get('title', ''))

        if not title:
            return jsonify({"error": "必须提供 'title' 参数。"}), 400

        song_ids = netease.search(title, artist)

        results = []
        # 使用ThreadPoolExecutor并发获取歌曲数据
        # max_workers 限制了最大并发线程数
        with ThreadPoolExecutor(max_workers=3) as executor:
            # executor.map 会将 fetch_song_data 函数应用到每个 song_id
            # 它会立即返回一个迭代器，并在后台并发执行任务
            future_results = executor.map(fetch_song_data, song_ids[:3])

            # 从结果中过滤掉因获取失败而返回的 None 值
            results = [res for res in future_results if res is not None]

        return jsonify(results)

    except Exception as e:
        print(f"发生错误: {e}")
        return jsonify({"error": "服务器内部错误，请稍后再试。"}), 500


@app.route("/")
def index():
    """
    服务主页。
    """
    return """
    <html>
    <head>
        <title>歌词搜索 API</title>
        <style>
            body { font-family: sans-serif; line-height: 1.6; padding: 2em; }
            h1 { color: #333; }
            p { color: #555; }
            code { background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>歌词搜索 API</h1>
        <p>这是一个歌词服务器。请使用 <code>/lyric</code> 接口来获取歌词。</p>
        <p>使用示例: <code>/lyric?title=歌曲名&artist=艺术家名</code></p>
    </body>
    </html>
    """


if __name__ == '__main__':
    from waitress import serve

    # 监听 0.0.0.0 地址，使其可以从网络访问
    serve(app, port=10492, host="0.0.0.0")