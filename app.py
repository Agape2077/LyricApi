from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
import netease
import qqmusic
import kugou

app = Flask(__name__)


def calculate_relevance_score(result, query_title, query_artist):
    """
    计算单个结果与查询词的相关性分数。
    """
    score = 0
    title = result.get('title', '').lower()
    artist = result.get('artist', '').lower()

    q_title = query_title.lower()
    q_artist = query_artist.lower()

    # 标题匹配计分
    if q_title in title:
        score += 2
    if title == q_title:  # 完全匹配额外加分
        score += 1

    # 艺术家匹配计分 (如果提供了艺术家)
    if q_artist:
        if q_artist in artist:
            score += 2
        if artist == q_artist:  # 完全匹配额外加分
            score += 1

    return score


def fetch_netease_data(song_id):
    """
    为单个网易云歌曲ID获取艺术家、标题和歌词。
    这是一个用于在线程池中执行的辅助函数。
    """
    try:
        # 增加健壮性检查：确保 song_id 是一个有效类型
        if not isinstance(song_id, (str, int)):
            print(f"接收到无效的网易云歌曲ID，类型为 {type(song_id)}: {song_id}")
            return None

        song_artist, song_title = netease.getInfo(song_id)
        # 如果获取信息失败，提前返回
        if not song_title:
            return None
        lyrics = netease.getLyric(song_id)
        # 检查是否真的获取到了歌词
        if "没有找到歌词" in lyrics:
            return None
        # 检查是否有翻译
        has_translation = "【" in lyrics
        # 在歌词前添加LRC格式的来源信息
        lyrics_with_source = f"[00:00.00]来源：网易云音乐\n{lyrics}"
        return {
            "source": "Netease",
            "id": str(song_id),
            "title": song_title,
            "artist": song_artist,
            "lyrics": lyrics_with_source,
            "has_translation": has_translation
        }
    except Exception as e:
        print(f"无法处理网易云歌曲ID {song_id}: {e}")
        return None


def fetch_qqmusic_data(song_info):
    """
    为单个QQ音乐歌曲获取歌词。
    这是一个用于在线程池中执行的辅助函数。
    """
    try:
        # 增加健壮性检查：确保 song_info 是一个字典
        if not isinstance(song_info, dict):
            print(f"接收到无效的QQ音乐歌曲信息，类型为 {type(song_info)}: {song_info}")
            return None

        lyrics = qqmusic.getLyric(song_info['songid'], song_info['songmid'])
        # 检查是否真的获取到了歌词
        if "未找到该歌曲的歌词" in lyrics:
            return None
        # 在歌词前添加LRC格式的来源信息
        lyrics_with_source = f"[00:00.00]来源：QQ音乐\n{lyrics}"
        return {
            "source": "QQMusic",
            "id": str(song_info['songid']),
            "title": song_info['title'],
            "artist": song_info['artist'],
            "lyrics": lyrics_with_source,
            "has_translation": False
        }
    except Exception as e:
        # 安全地记录错误，避免在except块中再次引发异常
        song_id_for_log = song_info.get('songid', '未知ID') if isinstance(song_info, dict) else song_info
        print(f"无法处理QQ音乐歌曲 {song_id_for_log}: {e}")
        return None


def fetch_kugou_data(song_info):
    """
    为单个酷狗音乐歌曲获取歌词。
    这是一个用于在线程池中执行的辅助函数。
    """
    try:
        # 增加健壮性检查：确保 song_info 是一个字典
        if not isinstance(song_info, dict):
            print(f"接收到无效的酷狗音乐歌曲信息，类型为 {type(song_info)}: {song_info}")
            return None

        lyrics = kugou.getLyric(song_info['hash'])
        # 检查是否真的获取到了歌词
        if "没有找到" in lyrics or "无法下载" in lyrics or "发生错误" in lyrics:
            return None
        # 在歌词前添加LRC格式的来源信息
        lyrics_with_source = f"[00:00.00]来源：酷狗音乐\n{lyrics}"
        return {
            "source": "Kugou",
            "id": song_info['hash'],
            "title": song_info['title'],
            "artist": song_info['artist'],
            "lyrics": lyrics_with_source,
            "has_translation": False
        }
    except Exception as e:
        # 安全地记录错误，避免在except块中再次引发异常
        song_hash_for_log = song_info.get('hash', '未知Hash') if isinstance(song_info, dict) else song_info
        print(f"无法处理酷狗音乐歌曲 {song_hash_for_log}: {e}")
        return None


@app.route("/lyric", methods=['GET'])
def get_data():
    """
    此接口用于聚合搜索歌词。
    接收 'artist' 和 'title' 作为查询参数。
    使用多线程并发从网易云、QQ音乐和酷狗获取最多各3首匹配歌曲的信息。
    """
    try:
        artist = str(request.args.get('artist', ''))
        title = str(request.args.get('title', ''))

        if not title:
            return jsonify({"error": "必须提供 'title' 参数。"}), 400

        # 在三个平台上搜索
        netease_song_ids = netease.search(title, artist)
        qq_songs_info = qqmusic.search(title, artist)
        kugou_songs_info = kugou.search(title, artist)

        all_results = []
        # 使用ThreadPoolExecutor并发获取所有歌曲数据
        with ThreadPoolExecutor(max_workers=9) as executor:
            netease_futures = executor.map(fetch_netease_data, netease_song_ids[:3])
            qqmusic_futures = executor.map(fetch_qqmusic_data, qq_songs_info[:3])
            kugou_futures = executor.map(fetch_kugou_data, kugou_songs_info[:3])

            all_results.extend([res for res in netease_futures if res is not None])
            all_results.extend([res for res in qqmusic_futures if res is not None])
            all_results.extend([res for res in kugou_futures if res is not None])

        # 为每个结果计算相关性得分
        for result in all_results:
            result['score'] = calculate_relevance_score(result, title, artist)

        # 按分数降序排序，分数相同时有翻译的优先
        all_results.sort(key=lambda x: (x.get('score', 0), x.get('has_translation', False)), reverse=True)

        # 在返回前移除临时键
        for result in all_results:
            if 'score' in result:
                del result['score']
            if 'has_translation' in result:
                del result['has_translation']

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
        <p>返回结果会包含一个 <code>source</code> 字段来区分来源 (<code>Netease</code>, <code>QQMusic</code>, 或 <code>Kugou</code>)。</p>
    </body>
    </html>
    """


if __name__ == '__main__':
    from waitress import serve

    serve(app, port=10492, host="0.0.0.0")
