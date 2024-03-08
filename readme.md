
## 请求
### 请求方式：Get
|配置项|位置|键|
|---- | ---- | --- | 
|基础地址|	URL	| -	|  
歌曲标题|	URL Params|	title	|
歌手名|	URL Params|	artist	|

返回：LRC内容

**最终组装地址： localhost:10492/lyric**




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




