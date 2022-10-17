import os
import time
import cv2
from base_camera import BaseCamera
import mediapipe as mp
from fuzzyfinder import fuzzyfinder


class Camera(BaseCamera):
    video_source = 0
    pTime = 0

    mp_draw = mp.solutions.drawing_utils
    mp_facemesh = mp.solutions.face_mesh
    facemesh = mp_facemesh.FaceMesh(max_num_faces=2)
    draw_spec = mp_draw.DrawingSpec(thickness=1, circle_radius=2)

    ear1prev = []
    ear2prev = []
    wordArray = []
    isLong = False
    blinkedFor = 0
    notBlinkedFor = 0
    timer = 0
    wasBlinked = False
    letterArray = ""
    letterIs = ""
    w = ""

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
                        Camera.isLong = True
                    else:
                        Camera.ear1prev.append(ear1)

                    if len(Camera.ear2prev) > 10:
                        Camera.ear2prev[count] = ear2
                        Camera.isLong = True
                    else:
                        Camera.ear2prev.append(ear2)

                    if Camera.isLong:
                        if ((Camera.ear1prev[abs(count-9)]*0.70 > ear1) and (Camera.ear2prev[abs(count-9)]*0.70 > ear2)):
                            # print("blink")
                            wasBlinked = True
                            Camera.blinkedFor = Camera.blinkedFor+1
                        else:
                            if (Camera.blinkedFor > (fps/2)):
                                # print("LONG blink")
                                Camera.letterArray = Camera.letterArray + "-"
                                yield "-"
                                Camera.blinkedFor = 0

                            elif (Camera.blinkedFor > int(fps/4)):
                                # print("SHORT blink")
                                Camera.letterArray = Camera.letterArray + "."
                                yield "."
                                Camera.blinkedFor = 0

                            else:

                                Camera.notBlinkedFor = Camera.notBlinkedFor+1
