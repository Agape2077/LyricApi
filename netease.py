import requests
import json
import io
import urllib.parse as urlparse


song_id = 700091

def getInfo(song_id):
    artist = ""
    song_info_url = f"https://music.163.com/api/song/detail/?id={song_id}&ids=[{song_id}]"
    response = requests.get(song_info_url,timeout=10)
    json_data = json.loads(response.text)['songs'][0]
    for i,obj in  enumerate(json_data['artists']):
        name = obj.get('name')
        artist += name
        if i < len(json_data['artists']) - 1:
            artist += "; "
    title = json_data["name"]
    return artist,title

def getLyric(song_id):
    lyric_url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1"
    response = requests.get(lyric_url,timeout=10)
    json_data = json.loads(response.text)
    origLyric = json_data["lrc"]["lyric"]
    if json_data["tlyric"]["version"]<=0:
        return origLyric
    transLyric = json_data["tlyric"]["lyric"]
    merged_lyrics = ""
    with  io.StringIO(origLyric) as  orig_lyrics, io.StringIO(transLyric) as trans_lyrics :
        orig_lyrics = orig_lyrics.readlines() 
        trans_lyrics = trans_lyrics.readlines()
        for i in range(len(orig_lyrics)):
            if not orig_lyrics[i].strip():
                continue
            orig_timestamp = orig_lyrics[i][1:orig_lyrics[i].index(']')]
            trans_timestamp, trans_lyric = None, ""
            for j in range(len(trans_lyrics)):
                if not trans_lyrics[j].strip():
                    continue
                curr_trans_timestamp = trans_lyrics[j][1:trans_lyrics[j].index(']')]
                if curr_trans_timestamp == orig_timestamp:
                    trans_timestamp = curr_trans_timestamp
                    trans_lyric = trans_lyrics[j].split(']')[-1].strip()
                    break
            if trans_lyric:
                merged_lyrics += f"[{orig_timestamp}] {orig_lyrics[i].split(']')[-1].strip()} 【{trans_lyric}】\n"
            else:
                merged_lyrics +=f"[{orig_timestamp}] {orig_lyrics[i].split(']')[-1].strip()}\n"

    return merged_lyrics


def search(song, artist):
    keywords_trans = urlparse.quote(str(song) + " " + str(artist), safe='')
    print("keyword:" + keywords_trans)
    response = requests.get(
        f"https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={keywords_trans}&type=1&offset=0&total=true&limit=20",
        timeout=10)
    data = json.loads(response.content)
    song_id = data['result']['songs'][0]['id']
    return song_id
