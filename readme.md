# LyricAPI
从网易云音乐获取歌词 并以lrc文件内容（后续会换成API的方式）呈现

## 使用方法
需要Python3 以上的环境。
克隆并安装依赖：
```shell
git clone https://github.com/Agape2077/LyricApi.git
pip install -r requirements.txt
```
运行：
```shell
python app.py
```



## 请求
### 请求方式：Get
|配置项|位置|键|
|---- | ---- | --- | 
|基础地址|	URL	| -	|  
歌曲标题|	URL Params|	title	|
歌手名|	URL Params|	artist	|

返回：LRC内容

**最终组装地址： localhost:10492/lyric**

 若需要添加公网访问，请将app.py中最后一行的127.0.0.1改为0.0.0.0或者自行配置转发。



# TODO:
使用更牛逼的Json进行返回，可以返回多条记录。
### 响应体：
**content-type: application/json**

### 返回格式

```json
[
    {
        "id": "string",
        "title": "title",
        "artist": "artist",
        "lyrics": "lrc content"
    },

...
]
```
|配置项|类型|键|说明|
|---- | ---- | --- | --- |
|艾迪|	string	| id | 可为字符串，用于与其他歌词去重 
歌曲标题|string|title|可与查询的结果不一致
歌手名|	string|	artist	|可与查询的结果不一致
歌词|string|lyrics|歌词文件内容




