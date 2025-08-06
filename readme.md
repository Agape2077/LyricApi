# LyricAPI
从网易云音乐获取歌词，并以API的方式呈现

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

### 响应体：
**content-type: application/json**

### 返回格式

```json
[
    {
        "id": "string",
        "title": "title",
        "artist": "artist",
        "lyrics": "lrc content",
        "source": "netease/qqmusic/kugou"
    }


]

```
为了防止被风控，每个服务只会获取三个结果


| 配置项  |类型| 键        |说明|
|------| ---- |----------| --- |
| id   |	string	| string   | 可为字符串，用于与其他歌词去重 
 歌曲标题 |string| title    |可与查询的结果不一致
 歌手名  |	string| 	artist	 |可与查询的结果不一致
 歌词   |string| lyrics   |歌词文件内容
来源|string|source|歌词来源




