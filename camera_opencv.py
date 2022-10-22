import os
import time
import cv2
from base_camera import BaseCamera
import mediapipe as mp


class Camera(BaseCamera):
    video_source = 0
    pTime = 0

    mp_draw = mp.solutions.drawing_utils
    mp_facemesh = mp.solutions.face_mesh
    facemesh = mp_facemesh.FaceMesh(max_num_faces=1)
    draw_spec = mp_draw.DrawingSpec(thickness=1, circle_radius=2)

    ear1prev = []
    ear2prev = []
    wordArray = []
    long_blink = False
    blink_timer = 0
    not_blink_timer = 0
    timer = 0
    has_blinked = False
    morse_code = ""
    DOT_THRESHOLD = 0.05
    LINE_THRESHOLD = 0.15

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def rescaleFrame(frame, percent=75):
        width = int(frame.shape[1] * percent / 100)
        height = int(frame.shape[0] * percent / 100)
        dim = (width, height)
        return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()
            # scaled = Camera.rescaleFrame(img, 150)
            scaled = img

            imgRGB = cv2.cvtColor(scaled, cv2.COLOR_BGR2RGB)
            results = Camera.facemesh.process(imgRGB)

            cTime = time.time()
            fps = 1/(cTime-Camera.pTime)
            Camera.pTime = cTime

            count = 0
            if results.multi_face_landmarks:
                for faceLm in results.multi_face_landmarks:
                    Camera.mp_draw.draw_landmarks(
                        scaled, faceLm, Camera.mp_facemesh.FACEMESH_CONTOURS, Camera.draw_spec, Camera.draw_spec)

                    ear1 = abs((faceLm.landmark[160].x-faceLm.landmark[144].x)**2-(faceLm.landmark[160].y-faceLm.landmark[144].y)**2)+abs((faceLm.landmark[158].x-faceLm.landmark[153].x)**2-(
                        faceLm.landmark[158].y-faceLm.landmark[153].y)**2)/abs(((faceLm.landmark[33].x-faceLm.landmark[133].x)**2)-((faceLm.landmark[33].y-faceLm.landmark[133].y)**2))
                    ear2 = abs((faceLm.landmark[385].x-faceLm.landmark[380].x)**2-(faceLm.landmark[385].y-faceLm.landmark[380].y)**2)+abs((faceLm.landmark[387].x-faceLm.landmark[373].x)**2-(
                        faceLm.landmark[387].y-faceLm.landmark[373].y)**2)/abs(((faceLm.landmark[362].x-faceLm.landmark[263].x)**2)-((faceLm.landmark[362].y-faceLm.landmark[263].y)**2))

                    if count > 10:
                        count = 0
                    else:
                        count = count + 1

                    if len(Camera.ear1prev) > 10:
                        Camera.ear1prev[count] = ear1
                        Camera.long_blink = True
                    else:
                        Camera.ear1prev.append(ear1)

                    if len(Camera.ear2prev) > 10:
                        Camera.ear2prev[count] = ear2
                        Camera.long_blink = True
                    else:
                        Camera.ear2prev.append(ear2)

                    if Camera.long_blink:
                        if ((Camera.ear1prev[abs(count-9)]*0.65 > ear1) and (Camera.ear2prev[abs(count-9)]*0.65 > ear2)):
                            # print("blink")
                            Camera.wasBlinked = True
                            Camera.blink_timer = Camera.blink_timer+1
                        else:
                            if (Camera.blink_timer > (fps*Camera.LINE_THRESHOLD)):
                                # print("LONG blink")
                                Camera.morse_code = Camera.morse_code + "-"
                                yield "-"
                                Camera.blink_timer = 0

                            elif (Camera.blink_timer > fps*Camera.DOT_THRESHOLD):
                                # print("SHORT blink")
                                Camera.morse_code = Camera.morse_code + "."
                                yield "."
                                Camera.blink_timer = 0

                            else:
                                if (Camera.not_blink_timer > fps):
                                    Camera.morse_code = ""
                                    Camera.not_blink_timer = 0
                                    yield ""
                                Camera.not_blink_timer = Camera.not_blink_timer+1
