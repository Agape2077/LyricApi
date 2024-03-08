from flask import Flask,request
import netease


app = Flask(__name__)

@app.route("/lyric", methods=['GET'])
def get_data():    
    artist =str(request.args.get('artist'))
    title = str(request.args.get('title'))
    if artist is None:
        artist = " "
    if title is None:
        title = " "
    return netease.getLyric(netease.search(title,artist))
@app.route("/")
def index():
    return """
<html>
<h1>
Hello!
</h1>
<p>this is a lyric server,please use it on App!</p>
</html>
"""

@app.route("/album")
def cover():
    return ""


if __name__ == '__main__':
    from waitress import serve
    serve(app,port=10492)
