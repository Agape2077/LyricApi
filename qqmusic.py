import requests
import json
import html
import base64


def search(song, artist):
    """
    根据歌曲和艺术家在QQ音乐搜索，返回一个包含歌曲信息的列表。
    """
    search_url = "https://c.y.qq.com/soso/fcgi-bin/search_cp"
    params = {
        "w": f"{song} {artist}",
        "n": 3,
        "t": 0,
        "aggr": 1,
        "cr": 1,
        "catZhida": 1,
        "lossless": 0,
        "flag_qc": 0,
        "p": 1,
        "format": "json",
        "inCharset": "utf8",
        "outCharset": "utf-8",
        "notice": 0,
        "platform": "yqq",
        "needNewCode": 0
    }

    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('code') == 0 and data['data']['song']['list']:
            song_list = data['data']['song']['list']
            results = []
            for item in song_list:
                # 拼接歌手名
                singer_names = '; '.join([singer['name'] for singer in item.get('singer', [])])
                results.append({
                    'songid': item['songid'],
                    'songmid': item['songmid'],
                    'title': item['songname'],
                    'artist': singer_names
                })
            return results
    except requests.RequestException as e:
        print(f"QQ音乐搜索请求失败: {e}")
    except KeyError as e:
        print(f"解析QQ音乐搜索结果失败，键错误: {e}")

    return []


def getLyric(songid, songmid):
    """
    根据QQ音乐的songid和songmid获取歌词。
    因网页端refer不推送中文歌词翻译，在此不做解析。
    """
    lyric_url = "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric.fcg"
    params = {
        "nobase64": 1,
        "musicid": songid,
        "format": "jsonp",
        "inCharset": "utf8",
        "outCharset": "utf-8"
    }

    # QQ音乐歌词接口需要Referer头
    headers = {
        'Referer': f'http://y.qq.com/portal/song/{songmid}.html'
    }

    try:
        response = requests.get(lyric_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        # 处理JSONP格式: "jsonp1({...})" -> "{...}"
        jsonp_text = response.text
        if jsonp_text.startswith('jsonp1(') and jsonp_text.endswith(')'):
            json_text = jsonp_text[len('jsonp1('):-1]
        else:
            # 兼容可能变化的callback名或纯JSON
            start = jsonp_text.find('(')
            end = jsonp_text.rfind(')')
            if start != -1 and end != -1:
                json_text = jsonp_text[start+1:end]
            else:
                json_text = jsonp_text

        lyric_data = json.loads(json_text)

        if lyric_data.get('code') == 0 and 'lyric' in lyric_data:
            # 返回的歌词是HTML实体编码的，需要解码
            return html.unescape(lyric_data['lyric'])
        else:
            return "未找到该歌曲的歌词。"

    except requests.RequestException as e:
        print(f"QQ音乐歌词请求失败: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"解析QQ音乐歌词结果失败: {e}")

    return "获取歌词时发生错误。"
