#
# Created on Jan 18, 2018
#
# @author: naxvm
#
# Based on @nuriaoyaga code:
# https://github.com/RoboticsURJC-students/2016-tfg-nuria-oyaga/blob/
#     master/gui/gui.py
#

import sys

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
import cv2

from Net.network import Detection_Network
from Net.threadnetwork import ThreadNetwork

class GUI(QtWidgets.QWidget):

    updGUI = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        ''' GUI class creates the GUI that we're going to use to
        preview the live video as well as the results of the real-time
        classification.
        '''

        self.network = Detection_Network() # ask for a model here (?)
        self.t_network = ThreadNetwork(self.network)
        self.t_network.start()

        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle("JdeRobot-TensorFlow detector")
        self.resize(1000, 600)
        self.move(150, 50)
        self.setWindowIcon(QtGui.QIcon('resources/jderobot.png'))
        self.updGUI.connect(self.update)

        # Original image label.
        self.im_label = QtWidgets.QLabel(self)
        self.im_label.resize(450, 350)
        self.im_label.move(25, 90)
        self.im_label.show()

        # Predicted image label.
        self.im_pred_label = QtWidgets.QLabel(self)
        self.im_pred_label.resize(450, 350)
        self.im_pred_label.move(525, 90)
        self.im_pred_label.show()

        # Button for configuring detection flow
        self.button_cont_detection = QtWidgets.QPushButton(self)
        self.button_cont_detection.move(300, 500)
        self.button_cont_detection.clicked.connect(self.toggleNetwork)

        # Button for processing a single frame
        self.button_one_frame = QtWidgets.QPushButton(self)
        self.button_one_frame.move(600, 500)
        self.button_one_frame.clicked.connect(self.updateOnce)
        self.button_one_frame.setText('On-demand detection')

        self.toggleNetwork()

        
    def setCamera(self, cam):
        ''' Declares the Camera object '''
        self.cam = cam

    def update(self):
        ''' Updates the GUI for every time the thread change '''
        # We get the original image and display it.
        im_prev = self.cam.getImage()
        self.network.input_image = im_prev

        im_predicted = self.network.output_image

        im = QtGui.QImage(im_prev.data, im_prev.shape[1], im_prev.shape[0],
                          QtGui.QImage.Format_RGB888)
        im_scaled = im.scaled(self.im_label.size())

        self.im_label.setPixmap(QtGui.QPixmap.fromImage(im_scaled))
        try:
            im_predicted = QtGui.QImage(im_predicted.data, im_predicted.shape[1], im_prev.shape[0],
                                        QtGui.QImage.Format_RGB888)
            im_predicted_scaled = im_predicted.scaled(self.im_pred_label.size())

            self.im_pred_label.setPixmap(QtGui.QPixmap.fromImage(im_predicted_scaled))
        except AttributeError:
            pass
        
    def toggleNetwork(self):
        self.t_network.activated = not self.t_network.activated

        if self.t_network.activated:
            self.button_cont_detection.setStyleSheet('QPushButton {color: red;}')
            self.button_cont_detection.setText('Switch off\nContinuous\nDetection')
        else:
            self.button_cont_detection.setStyleSheet('QPushButton {color: green;}')
            self.button_cont_detection.setText('Switch on\nContinuous\nDetection')

    def updateOnce(self):
        self.t_network.runOnce()