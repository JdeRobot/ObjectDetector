#
# Created on Jan, 2018
#
# @author: naxvm
#
# Class which abstracts a Camera from a proxy (created by ICE/ROS),
# and provides the methods to keep it constantly updated. Also, delivers it
# to the neural network, which returns returns the same image with the
# detected classes and scores, and the bounding boxes drawn on it.
#

import traceback
import threading
import cv2

class Camera:

    def __init__ (self, device_idx):
        ''' Camera class gets images from a video device and transform them
        in order to detect objects in the image.
        '''
        self.lock = threading.Lock()
        self.cam = cv2.VideoCapture(device_idx)
        self.im_width = self.cam.get(3)
        self.im_height = self.cam.get(4)


    def getImage(self):
        ''' Gets the image from the webcam and returns it. '''
        return self.image

    def update(self):
        ''' Updates the camera with a frame from the device every time the thread changes. '''
        if self.cam:
            self.lock.acquire()
            _, frame = self.cam.read()
            self.image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.lock.release()
