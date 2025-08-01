import requests
import json
import base64
import zlib

# KRC解码密钥
KRC_KEYS = [64, 71, 97, 119, 94, 50, 116, 71, 81, 54, 49, 45, 206, 210, 110, 105]


def search(song, artist):
    """
    根据歌曲和艺术家在酷狗搜索，返回一个包含歌曲信息的列表。
    """
    search_url = "http://ioscdn.kugou.com/api/v3/search/song"
    params = {
        "keyword": f"{song} {artist}",
        "page": 1,
        "pagesize": 3,
        "showtype": 10,
        "plat": 2,
        "version": 7910,
        "tag": 1,
        "correct": 1,
        "privilege": 1,
        "sver": 5
    }

    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('errcode') == 0 and data['data']['info']:
            song_list = data['data']['info']
            results = []
            for item in song_list:
                results.append({
                    'hash': item['hash'],
                    'title': item['songname'],
                    'artist': item['singername']
                })
            return results
    except requests.RequestException as e:
        print(f"酷狗搜索请求失败: {e}")
    except (KeyError, json.JSONDecodeError) as e:
        print(f"解析酷狗搜索结果失败，键错误: {e}")

    return []


def _decode_krc_lyric(encoded_content):
    """解码KRC格式的歌词。"""
    decoded_bytes = base64.b64decode(encoded_content)
    if not decoded_bytes.startswith(b'krc18'):
        # 兼容非KRC格式（LRC）的回退方案
        return decoded_bytes.decode('utf-8', errors='ignore')

    key_len = len(KRC_KEYS)
    decrypted_data = bytearray()
    for i in range(4, len(decoded_bytes)):
        decrypted_data.append(decoded_bytes[i] ^ KRC_KEYS[(i - 4) % key_len])

    try:
        # 解压zlib数据
        return zlib.decompress(decrypted_data).decode('utf-8', errors='ignore')
    except zlib.error as e:
        print(f"Zlib解压失败: {e}")
        return "解压KRC歌词失败。"


def getLyric(song_hash):
    """
    根据给定的酷狗歌曲哈希获取歌词。
    """
    preview_url = f"https://krcs.kugou.com/search?ver=1&man=yes&client=mobi&keyword=&duration=&hash={song_hash}"

    try:
        preview_response = requests.get(preview_url, timeout=10)
        preview_response.raise_for_status()
        preview_data = preview_response.json()

        if preview_data.get('status') != 200 or not preview_data.get('candidates'):
            return "这首歌没有找到候选歌词。"

        candidates = preview_data['candidates']

        # 优先选择官方歌词，否则回退到第三方
        best_candidate = next((c for c in candidates if c.get('product_from') == '官方推荐歌词'), None)
        if not best_candidate:
            best_candidate = candidates[0]

        lyric_id = best_candidate['id']
        accesskey = best_candidate['accesskey']

        # 下载实际的歌词内容
        download_url = f"https://lyrics.kugou.com/download?ver=1&client=pc&id={lyric_id}&accesskey={accesskey}&fmt=lrc&charset=utf8"
        lyric_response = requests.get(download_url, timeout=10)
        lyric_response.raise_for_status()
        lyric_data = lyric_response.json()

        if lyric_data.get('status') == 200 and 'content' in lyric_data:
            return _decode_krc_lyric(lyric_data['content'])
        else:
            return "无法下载歌词内容。"

    except requests.RequestException as e:
        print(f"酷狗歌词请求失败: {e}")
    except (KeyError, json.JSONDecodeError) as e:
        print(f"解析酷狗歌词结果失败: {e}")

    return "获取酷狗歌词时发生错误。"

