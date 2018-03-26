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

from Net.utils import visualization_utils as vis_util
import numpy as np


class GUI(QtWidgets.QWidget):

    updGUI = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        ''' GUI class creates the GUI that we're going to use to
        preview the live video as well as the results of the real-time
        classification.
        '''
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle("JdeRobot-TensorFlow detector")
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

    def setCamera(self, cam, t_cam):
        ''' Declares the Camera object '''
        self.cam = cam
        self.t_cam = t_cam


    def setNetwork(self, network, t_network):
        ''' Declares the Network object and its corresponding control thread. '''
        self.network = network
        # Copy the category index fetched from the network
        self.category_index = self.network.category_index
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
        detection_boxes = self.network.boxes
        detection_scores = self.network.scores
        detection_classes = self.network.classes
        num_detections = self.network.num

        image_np = np.copy(self.im_prev)


        vis_util.visualize_boxes_and_labels_on_image_array(
        				image_np,
        				np.squeeze(detection_boxes),
        				np.squeeze(detection_classes).astype(np.int32),
        				np.squeeze(detection_scores),
        				self.category_index,
        				use_normalized_coordinates=True,
        				line_thickness=6)



        im = QtGui.QImage(image_np.data, image_np.shape[1], image_np.shape[0],
                          QtGui.QImage.Format_RGB888)

        im_drawn = im.scaled(self.im_label.size())
        self.im_pred_label.setPixmap(QtGui.QPixmap.fromImage(im_drawn))
