#!/usr/bin/env python
from flask import Flask, make_response, render_template, Response, request
from flask_cors import CORS, cross_origin
# import camera driver
# if os.environ.get('CAMERA'):
#     Camera = import_module('camera_' + os.environ['CAMERA']).Camera
# else:
#     from camera import Camera
from camera_opencv import Camera
import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__, static_url_path='/static')
cors = CORS(app)


@app.route('/')
@cross_origin()
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    # yield b'--frame\r\n'
    frame = camera.get_frame()
    yield frame
    # yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/camera_feed')
@cross_origin()
def camera_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    # return Response(gen(Camera()),
    #                 mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(gen(Camera()),
                    mimetype='text')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)
