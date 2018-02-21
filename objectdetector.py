#
# Created on Oct, 2017
#
# @author: naxvm
#
# It receives images from a live video and classify them into digits 
# employing a convolutional neural network, based on TensorFlow Deep Learning middleware.
# It shows the live video and the results in a GUI.
#
# Based on @nuriaoyaga code:
# https://github.com/RoboticsURJC-students/2016-tfg-nuria-oyaga/blob/
#     master/numberclassifier.py
# and @dpascualhe's:
# https://github.com/RoboticsURJC-students/2016-tfg-david-pascual/blob/
#     master/digitclassifier.py
#
#

import sys
import signal

from PyQt5 import QtWidgets

from Camera.camera import Camera
from Camera.threadcamera import ThreadCamera
from GUI.gui import GUI
from GUI.threadgui import ThreadGUI

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':

    cam = Camera()

    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    window.setCamera(cam)
    window.show()
    
    # Threading camera
    t_cam = ThreadCamera(cam)
    t_cam.start()
    
    # Threading GUI
    t_gui = ThreadGUI(window)
    t_gui.start()
    
    sys.exit(app.exec_())

