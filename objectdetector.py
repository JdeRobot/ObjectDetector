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

from Camera.threadcamera import ThreadCamera
from GUI.gui import GUI
from GUI.threadgui import ThreadGUI
from Net.threadnetwork import ThreadNetwork

import config
import comm

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':

    try:
        cfg = config.load(sys.argv[1])
    except IndexError:
        raise SystemExit('Missing YML file. Usage: python2 objectdetector.py objectdetector.yml')

    ##################################################
    ################ SOURCE CHOICE ###################
    ##################################################
    source = cfg.getProperty('ObjectDetector.Source')

    if source.lower() == 'local':
        from Camera.local_camera import Camera
        cam_idx = cfg.getProperty('ObjectDetector.Local.DeviceNo')
        print('  Chosen source: local camera (index %d)' % (cam_idx))
        cam = Camera(cam_idx)
    elif source.lower() == 'video':
        from Camera.local_video import Camera
        video_path = cfg.getProperty('ObjectDetector.Video.Path')
        print('  Chosen source: local video (%s)' % (video_path))
        cam = Camera(video_path)
    elif source.lower() == 'stream':
        # comm already prints the source technology (ICE/ROS)
        jdrc = comm.init(cfg, 'ObjectDetector')
        proxy = jdrc.getCameraClient('ObjectDetector.Stream')
        from Camera.stream_camera import Camera
        cam = Camera(proxy)
    else:
        raise SystemExit(('%s not supported! Supported source: Local, Video, Stream') % (source))

    ##################################################
    ############### FRAMEWORK CHOICE #################
    ##################################################
    net_prop = cfg.getProperty('ObjectDetector.Network')
    framework = net_prop['Framework']
    if framework.lower() == 'tensorflow':
        from Net.TensorFlow.network import DetectionNetwork
    elif framework.lower() == 'keras':
        sys.path.append('Net/Keras')
        from Net.Keras.network import DetectionNetwork
    else:
        raise SystemExit(('%s not supported! Supported frameworks: Keras, TensorFlow') % (framework))

    # Threading the camera...
    t_cam = ThreadCamera(cam)
    t_cam.start()

    network = DetectionNetwork(net_prop)
    network.setCamera(cam)
    t_network = ThreadNetwork(network)
    t_network.start()

    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    window.setCamera(cam, t_cam)
    window.setNetwork(network, t_network)
    window.show()

    # Threading GUI
    t_gui = ThreadGUI(window)
    t_gui.start()


    print("")
    print("Requested timers:")
    print("    Camera: %d ms" % (t_cam.t_cycle))
    print("    GUI: %d ms" % (t_gui.t_cycle))
    print("    Network: %d ms" % (t_network.t_cycle))
    print("")

    sys.exit(app.exec_())
