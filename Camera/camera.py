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

import os
import sys
import random
import traceback
import threading

import cv2
import numpy as np
import tensorflow as tf

class Camera:

    def __init__ (self, cam):
        ''' Camera class gets images from live video and transform them
        in order to predict the digit in the image.
        '''
        status = 0

<<<<<<< HEAD
        self.cam = cam
=======
        # Creation of the camera through the comm-ICE proxy.
        try:
            cfg = config.load(sys.argv[1])
        except IndexError:
            raise SystemExit('Missing YML file. Usage: python2 objectdetector.py objectdetector.yml')
        
        jdrc = comm.init(cfg, 'ObjectDetector')


        self.net_model = cfg.getNode()['Model']
>>>>>>> 0b212de57763b36ab616dbd991f58c6e9e3bbe7a

        self.lock = threading.Lock()

        try:
            if self.cam.hasproxy():
                self.im = self.cam.getImage()
                self.im_height = self.im.height
                self.im_width = self.im.width
                
                print('Image size: {0}x{1} px'.format(
                        self.im_width, self.im_height))
            else:
                print("Interface camera not connected")

        except:
            traceback.print_exc()
            exit()
            status = 1

    def getImage(self):
        ''' Gets the image from the webcam and returns it. '''
        if self.cam:
            self.lock.acquire()
            im = np.zeros((self.im_height, self.im_width, 3), np.uint8)
            im = np.frombuffer(self.im.data, dtype=np.uint8)
            im = np.reshape(im, (self.im_height, self.im_width, 3))

            self.lock.release()

            return im

    def update(self):
        ''' Updates the camera every time the thread changes. '''
        if self.cam:
            self.lock.acquire()

            self.im = self.cam.getImage()
            self.im_height = self.im.height
            self.im_width = self.im.width

            self.lock.release()
