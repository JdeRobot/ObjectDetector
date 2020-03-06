#
# Created on Jan, 2018
#
# @author: naxvm
#
# Class which abstracts a Camera from a local video file,
# and provides the methods to keep it constantly updated. Also, delivers it
# to the neural network, which returns returns the same image with the
# detected classes and scores, and the bounding boxes drawn on it.
#

import traceback
import threading
import cv2
from os import path
import numpy as np

class Camera:

    def __init__ (self, video_path):
        ''' Camera class gets images from a video device and transform them
        in order to detect objects in the image.
        '''
        self.lock = threading.Lock()

        self.cam = cv2.VideoCapture(video_path)
        self.stop = False
        if not self.cam.isOpened():
            cprint.fatal(f'{video_path} is not a valid video file. Please check the video file', interrupt=True)

        self.im_width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.im_height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # Initial placeholder
        self.image = np.zeros((self.im_width, self.im_height, 3))

    def getImage(self):
        ''' Gets the image from the webcam and returns it. '''
        return self.image

    def update(self):
        ''' Updates the camera with a frame from the device every time the thread changes. '''
        if self.cam:
            self.lock.acquire()
            ret, frame = self.cam.read()
            if ret:
                self.image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                self.stop = True
            self.lock.release()
