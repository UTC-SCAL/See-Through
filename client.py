"""."""
from flask import Flask, render_template, Response
from camera import VideoCamera
import time

app = Flask(__name__)

@app.route('/')
def index():
    """Where the server URL directs to."""
    return render_template('index.html')


def gen(camera):
    """A generator for the web cam."""
    counter = 0;
    while True:
        frame = camera.get_frame()
        counter += 1
        to_send = 'Current Time is: {} Current Frame is: {}END FRAME NUM'.format("%.2f" % time.time(), counter)
        yield (b'Sent-Time: ' + bytes(to_send, 'utf-8') + b'\n'
               b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    """."""
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='', port=5000, debug=False)
