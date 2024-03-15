from servers import Camera, Audio
from flask import Flask, Response, render_template_string, stream_with_context


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


def gen_audio(audio):
    while True:
        data = audio.get_audio()
        yield (data)


app = Flask(__name__)


@app.route("/video_feed")
def video_feed():
    return Response(gen(Camera()), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/audio_feed")
def audio_feed():
    return Response(stream_with_context(gen_audio(Audio())))


@app.route("/")
def index():
    global modle
    video_tag = """<img src="{{ url_for('video_feed') }}">"""
    audio_tag = """<audio autoplay visibility="hidden"><source src="{{url_for('audio_feed')}}" type="audio/x-wav;codec=pcm">Your browser does not support the audio element.</audio>"""

    tags = {0: video_tag + audio_tag, 1: audio_tag, 2: video_tag}

    content = tags[modle]

    return render_template_string(
        """<html>
    <head>
        <title>{title}</title>
        <link rel="icon" href="data:image/svg+xml;base64,CjxzdmcgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB2aWV3Qm94PSIwIDAgNTAgNTAiPgogICAgPGNpcmNsZSBjeD0iMjUiIGN5PSIyNSIgcj0iMjAiIGZpbGw9InJlZCIgLz4KPC9zdmc+Cg==">
    </head>
    <body>{content}</body>
    </html>""".format(
            title=["Intranet Broadcast", "Audio Sharing", "Screen Sharing"][modle],
            content=content,
        )
    )


if __name__ == "__main__":
    local_host = "127.0.0.1"
    ip_host = "0.0.0.0"
    port = 8001
    modle = int(input("Please select the mode: 0 for Intranet Broadcast, 1 for Audio Sharing, 2 for Screen Sharing: "))
    app.run(threaded=True, host=ip_host, port=port)