#
# Created on Oct, 2017
#
#
#
# Based on @nuriaoyaga code:
# https://github.com/RoboticsURJC-students/2016-tfg-nuria-oyaga/blob/
#     master/numberclassifier.py
# and @dpascualhe's:
# https://github.com/RoboticsURJC-students/2016-tfg-david-pascual/blob/
#     master/digitclassifier.py
#
#

__author__ = 'naxvm'

import argparse
import signal
import sys
from PyQt5 import QtWidgets

import utils
from Camera.threadcamera import ThreadCamera
from cprint import cprint
from GUI.gui import GUI
from GUI.threadgui import ThreadGUI
from Net.detection_network import DetectionNetwork
from Net.threadnetwork import ThreadNetwork

signal.signal(signal.SIGINT, signal.SIG_DFL)


if __name__ == '__main__':
    # Parameter parsing
    descr = '''
    Receives images from a video source and run neural detection inferences on
    the provided images. Shows the results in a GUI.'''
    parser = argparse.ArgumentParser(description=descr)
    parser.add_argument('config_file', type=str, help='Path for the YML configuration file')
    args = parser.parse_args()

    source, cam_params, net_params = utils.readConfig(args.config_file)

    # Camera
    cam = utils.getVideoSource(source, cam_params)
    cprint.ok('Camera ready')

    # Threading the camera...
    t_cam = ThreadCamera(cam)
    t_cam.start()

    # Inference network
    net = DetectionNetwork(net_params)
    net.setCamera(cam)
    cprint.ok('Network ready')

    # Threading the network...
    t_network = ThreadNetwork(net)
    t_network.start()

    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    window.setCamera(cam, t_cam)
    window.setNetwork(net, t_network)
    window.show()

    # Threading GUI
    t_gui = ThreadGUI(window)
    t_gui.start()

    # print("")
    # print("Requested timers:")
    # print("    Camera: %d ms" % (t_cam.t_cycle))
    # print("    GUI: %d ms" % (t_gui.t_cycle))
    # print("    Network: %d ms" % (t_network.t_cycle))
    # print("")

    sys.exit(app.exec_())
