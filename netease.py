import requests
import json
import io
import urllib.parse as urlparse


def getInfo(song_id):
    """
    根据给定的歌曲ID获取艺术家和标题。
    """
    artist = ""
    song_info_url = f"https://music.163.com/api/song/detail/?id={song_id}&ids=[{song_id}]"
    # 使用 session 以实现潜在的连接池复用
    with requests.Session() as s:
        response = s.get(song_info_url, timeout=10)
        response.raise_for_status()  # 如果HTTP状态码是4xx/5xx，则抛出异常
        json_data = response.json()['songs'][0]

    for i, obj in enumerate(json_data['artists']):
        name = obj.get('name')
        artist += name
        if i < len(json_data['artists']) - 1:
            artist += "; "
    title = json_data["name"]
    return artist, title


def getLyric(song_id):
    """
    根据给定的歌曲ID获取并合并原始歌词和翻译歌词。
    """
    lyric_url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1"
    with requests.Session() as s:
        response = s.get(lyric_url, timeout=10)
        response.raise_for_status()
        json_data = response.json()

    # 检查是否有歌词
    if "lrc" not in json_data or not json_data["lrc"]["lyric"]:
        return "这首歌没有找到歌词。"

    origLyric = json_data["lrc"]["lyric"]

    # 如果没有翻译歌词，直接返回原文歌词
    if "tlyric" not in json_data or not json_data["tlyric"]["lyric"]:
        return origLyric

    transLyric = json_data["tlyric"]["lyric"]

    # 创建一个字典来映射时间戳和翻译歌词，以提高查找效率
    trans_map = {}
    for line in io.StringIO(transLyric).readlines():
        if ']' in line:
            try:
                timestamp = line[1:line.index(']')]
                lyric_text = line.split(']')[-1].strip()
                if lyric_text:
                    trans_map[timestamp] = lyric_text
            except ValueError:
                continue  # 跳过没有有效时间戳的行

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
                merged_lyrics += line  # 保留没有时间戳的行 (例如元数据)
        else:
            merged_lyrics += line

    return merged_lyrics.strip()


def search(song, artist):
    """
    根据歌曲和艺术家搜索，返回一个歌曲ID的列表。
    """
    # 确保关键词被正确地URL编码
    keywords_trans = urlparse.quote(f"{song} {artist}")
    search_url = (
        f"https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={keywords_trans}"
        "&type=1&offset=0&total=true&limit=20"
    )

    with requests.Session() as s:
        response = s.get(search_url, timeout=10)
        response.raise_for_status()
        data = response.json()

    if data.get('result', {}).get('songCount', 0) > 0:
        # 从搜索结果中提取所有歌曲的ID，并返回一个列表
        song_ids = [s['id'] for s in data['result']['songs']]
        return song_ids
    return []