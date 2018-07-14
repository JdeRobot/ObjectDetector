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
import yaml

from PyQt5 import QtWidgets

from Camera.threadcamera import ThreadCamera
from GUI.gui import GUI
from GUI.threadgui import ThreadGUI
from Net.threadnetwork import ThreadNetwork

signal.signal(signal.SIGINT, signal.SIG_DFL)

def selectVideoSource(cfg):
    """
    @param cfg: configuration
    @return cam: selected camera
    @raise SystemExit in case of unsupported video source
    """
    source = cfg['ObjectDetector']['Source']
    if source.lower() == 'local':
        from Camera.local_camera import Camera
        cam_idx = cfg['ObjectDetector']['Local']['DeviceNo']
        print('  Chosen source: local camera (index %d)' % (cam_idx))
        cam = Camera(cam_idx)
    elif source.lower() == 'video':
        from Camera.local_video import Camera
        video_path = cfg['ObjectDetector']['Video']['Path']
        print('  Chosen source: local video (%s)' % (video_path))
        cam = Camera(video_path)
    elif source.lower() == 'stream':
        # comm already prints the source technology (ICE/ROS)
        import comm
        import config
        cfg = config.load(sys.argv[1])
        jdrc = comm.init(cfg, 'ObjectDetector')
        proxy = jdrc.getCameraClient('ObjectDetector.Stream')
        from Camera.stream_camera import Camera
        cam = Camera(proxy)
    elif source == 'ROS':
        from Camera.ros_camera import Camera
        topic = cfg['ObjectDetector']['ROS']['Topic']
        format = cfg['ObjectDetector']['ROS']['Format']
        cam = Camera(topic, format)
    else:
        raise SystemExit(('%s not supported! Supported source:'
                          'Local, Video, Stream, ROS') % (source))

    return cam

def selectNetwork(cfg):
    """
    @param cfg: configuration
    @return net_prop, DetectionNetwork: network properties and Network class
    @raise SystemExit in case of invalid network
    """
    net_prop = cfg['ObjectDetector']['Network']
    framework = net_prop['Framework']
    if framework.lower() == 'tensorflow':
        from Net.TensorFlow.network import DetectionNetwork
    elif framework.lower() == 'keras':
        sys.path.append('Net/Keras')
        from Net.Keras.network import DetectionNetwork
    else:
        raise SystemExit(('%s not supported! Supported frameworks: Keras, TensorFlow') % (framework))
    return net_prop, DetectionNetwork

def readConfig():
    try:
        with open(sys.argv[1], 'r') as stream:
            return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        raise SystemExit('Error: Cannot read/parse YML file. Check YAML syntax.')
    except:
        raise SystemExit('\n\tUsage: python2 objectdetector.py objectdetector.yml\n')

if __name__ == '__main__':

    cfg = readConfig()
    cam = selectVideoSource(cfg)
    net_prop, DetectionNetwork = selectNetwork(cfg)

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
