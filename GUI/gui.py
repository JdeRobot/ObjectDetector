#
# Created on Jan 18, 2018
#
# @author: naxvm
#
# Based on @nuriaoyaga code:
# https://github.com/RoboticsURJC-students/2016-tfg-nuria-oyaga/blob/
#     master/gui/gui.py
#


from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets


import numpy as np
import cv2
from Net.utils import label_map_util


COLORS = label_map_util.COLORS



class GUI(QtWidgets.QWidget):

    updGUI = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        ''' GUI class creates the GUI that we're going to use to
        preview the live video as well as the results of the real-time
        classification.
        '''
        QtWidgets.QWidget.__init__(self, parent)
        self.resize(1200, 500)
        self.move(150, 50)
        self.setWindowIcon(QtGui.QIcon('GUI/resources/jderobot.png'))
        self.updGUI.connect(self.update)

        # Original image label.
        self.im_label = QtWidgets.QLabel(self)
        self.im_label.resize(450, 350)
        self.im_label.move(25, 90)
        self.im_label.show()

        # Video capture framerate label.
        self.video_framerate_label = QtWidgets.QLabel(self)
        self.video_framerate_label.move(220, 450)
        self.video_framerate_label.resize(50, 40)
        self.video_framerate_label.show()

        # Processed image label.
        self.im_pred_label = QtWidgets.QLabel(self)
        self.im_pred_label.resize(450, 350)
        self.im_pred_label.move(725, 90)
        self.im_pred_label.show()

        # Prediction framerate label.
        self.predict_framerate_label = QtWidgets.QLabel(self)
        self.predict_framerate_label.move(930, 450)
        self.predict_framerate_label.resize(50,40)
        self.predict_framerate_label.show()

        # Button for configuring detection flow
        self.button_cont_detection = QtWidgets.QPushButton(self)
        self.button_cont_detection.move(550, 100)
        self.button_cont_detection.clicked.connect(self.toggleNetwork)
        self.button_cont_detection.setText('Continuous')
        self.button_cont_detection.setStyleSheet('QPushButton {color: green;}')

        # Button for processing a single frame
        self.button_one_frame = QtWidgets.QPushButton(self)
        self.button_one_frame.move(555, 200)
        self.button_one_frame.clicked.connect(self.updateOnce)
        self.button_one_frame.setText('Step')

        # Logo
        self.logo_label = QtWidgets.QLabel(self)
        self.logo_label.resize(150, 150)
        self.logo_label.move(520, 300)
        self.logo_label.setScaledContents(True)

        logo_img = QtGui.QImage()
        logo_img.load('GUI/resources/jderobot.png')
        self.logo_label.setPixmap(QtGui.QPixmap.fromImage(logo_img))
        self.logo_label.show()

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.scale = 3

        self.setWindowTitle("JdeRobot - ObjectDetector")


    def setCamera(self, cam, t_cam):
        ''' Declares the Camera object '''
        self.cam = cam
        self.t_cam = t_cam


    def setNetwork(self, network, t_network):
        ''' Declares the Network object and its corresponding control thread. '''
        self.network = network
        # We create the color dictionary for the bounding boxes.
        self.net_classes = self.network.classes
        self.colors = {}
        idx = 0
        for _class in self.net_classes.values():
            self.colors[_class] = COLORS[idx]
            idx =+ 1

        self.t_network = t_network


    def update(self):
        ''' Updates the GUI for every time the thread change '''
        # We get the original image and display it.
        self.im_prev = self.cam.getImage()
        im = QtGui.QImage(self.im_prev.data, self.im_prev.shape[1], self.im_prev.shape[0],
                          QtGui.QImage.Format_RGB888)
        self.im_scaled = im.scaled(self.im_label.size())

        self.im_label.setPixmap(QtGui.QPixmap.fromImage(self.im_scaled))

        if self.t_network.is_activated:
            self.renderModifiedImage()

        self.predict_framerate_label.setText("%d fps" % (self.t_network.framerate))
        self.video_framerate_label.setText("%d fps" % (self.t_cam.framerate))


    def toggleNetwork(self):
        self.t_network.toggle()

        if self.t_network.is_activated:
            self.button_cont_detection.setStyleSheet('QPushButton {color: green;}')
        else:
            self.button_cont_detection.setStyleSheet('QPushButton {color: red;}')

    def updateOnce(self):
        self.t_network.runOnce()
        self.renderModifiedImage()


    def renderModifiedImage(self):
        factor = 2
        new_size = (self.cam.im_width*factor, self.cam.im_height*factor)
        image_np = cv2.resize(np.copy(self.im_prev), new_size)

        detection_boxes = self.network.boxes
        detection_classes = self.network.predictions
        detection_scores = self.network.scores

        for index in range(len(detection_classes)):
            _class = detection_classes[index]
            score = detection_scores[index]
            rect = detection_boxes[index]
            xmin = rect[0] * factor
            ymin = rect[1] * factor
            xmax = rect[2] * factor
            ymax = rect[3] * factor
            cv2.rectangle(image_np, (xmin, ymax), (xmax, ymin), self.colors[_class], 3)

            label = "{0} ({1} %)".format(_class, int(score*100))
            [size, base] = cv2.getTextSize(label, self.font, self.scale, 2)

            points = np.array([[[xmin, ymin + base],
                                [xmin, ymin - size[1]],
                                [xmin + size[0], ymin - size[1]],
                                [xmin + size[0], ymin + base]]], dtype=np.int32)
            cv2.fillPoly(image_np, points, (0, 0, 0))
            cv2.putText(image_np, label, (xmin, ymin), self.font, self.scale, (255, 255, 255), 2)

        im = QtGui.QImage(image_np.data, image_np.shape[1], image_np.shape[0],
                          QtGui.QImage.Format_RGB888)

        im_drawn = im.scaled(self.im_label.size())
        self.im_pred_label.setPixmap(QtGui.QPixmap.fromImage(im_drawn))
