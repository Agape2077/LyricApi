import requests
import json
import io


def getInfo(song_id):
    """
    根据给定的歌曲ID获取艺术家和标题。
    """
    try:
        artist = ""
        song_info_url = f"https://music.163.com/api/song/detail/?id={song_id}&ids=[{song_id}]"
        with requests.Session() as s:
            response = s.get(song_info_url, timeout=10)
            response.raise_for_status()
            json_response = response.json()

        if not isinstance(json_response, dict):
            print(f"网易云 getInfo for ID {song_id} 返回的不是一个有效的JSON对象: {json_response}")
            return "", ""

        songs_list = json_response.get('songs')
        if not isinstance(songs_list, list) or not songs_list:
            print(f"网易云 getInfo for ID {song_id} 返回无效数据: {json_response}")
            return "", ""

        json_data = songs_list[0]
        if not isinstance(json_data, dict):
            print(f"网易云 getInfo for ID {song_id} 返回的歌曲条目格式错误")
            return "", ""

        artists_list = json_data.get('artists', [])
        if not isinstance(artists_list, list):
            artists_list = []

        for i, obj in enumerate(artists_list):
            if isinstance(obj, dict):
                name = obj.get('name')
                if name:
                    artist += name
                    if i < len(artists_list) - 1:
                        artist += "; "
        title = json_data.get("name", "")
        return artist, title
    except Exception as e:
        print(f"网易云 getInfo for ID {song_id} 发生内部错误: {e}")
        return "", ""  # 在任何异常时返回安全的默认值


def getLyric(song_id):
    """
    根据给定的歌曲ID获取并合并原始歌词和翻译歌词。
    """
    try:
        lyric_url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1"
        with requests.Session() as s:
            response = s.get(lyric_url, timeout=10)
            response.raise_for_status()
            json_data = response.json()

        if not isinstance(json_data, dict):
            return "获取歌词时发生错误。"

        lrc_data = json_data.get("lrc")
        if not isinstance(lrc_data, dict) or not lrc_data.get("lyric"):
            return "这首歌没有找到歌词。"

        origLyric = lrc_data["lyric"]

        tlyric_data = json_data.get("tlyric")
        if not isinstance(tlyric_data, dict) or not tlyric_data.get("lyric"):
            return origLyric

        transLyric = tlyric_data["lyric"]

        trans_map = {}
        for line in io.StringIO(transLyric).readlines():
            if ']' in line:
                try:
                    timestamp = line[1:line.index(']')]
                    lyric_text = line.split(']')[-1].strip()
                    if lyric_text:
                        trans_map[timestamp] = lyric_text
                except ValueError:
                    continue

        merged_lyrics = ""
        for line in io.StringIO(origLyric).readlines():
            if ']' in line:
                try:
                    timestamp = line[1:line.index(']')]
                    orig_text = line.split(']')[-1].strip()
                    trans_text = trans_map.get(timestamp)

                    merged_lyrics += f"[{timestamp}] {orig_text}"
                    if trans_text:
                        merged_lyrics += f" 【{trans_text}】"
                    merged_lyrics += "\n"
                except ValueError:
                    merged_lyrics += line
            else:
                merged_lyrics += line

        return merged_lyrics.strip()
    except Exception as e:
        print(f"网易云 getLyric for ID {song_id} 发生内部错误: {e}")
        return "获取歌词时发生错误。"


def search(song, artist):
    """
    根据歌曲和艺术家搜索，返回一个歌曲ID的列表。
    """
    try:
        search_url = "https://music.163.com/api/search/get/web"
        params = {
            "s": f"{song} {artist}",
            "type": 1,
            "offset": 0,
            "total": "true",
            "limit": 20
        }

        with requests.Session() as s:
            response = s.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

        if not isinstance(data, dict):
            return []

        if data.get('result', {}).get('songCount', 0) > 0:
            song_list = data.get('result', {}).get('songs', [])
            if not isinstance(song_list, list):
                return []
            song_ids = [s['id'] for s in song_list if isinstance(s, dict) and 'id' in s]
            return song_ids
        return []
    except Exception as e:
        print(f"网易云 search 发生内部错误: {e}")
        return []
