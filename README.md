# ObjectDetector

### Contents

1. [Introduction](#introduction)
2. [Getting started](#getting-started)
3. [Requirements](#requirements)
4. [How to use](#how-to-use)
5. [Framework choice](#framework-choice)
## Introduction

`dl-objectdetector` is a JdeRobot node, composed of 3 entities: `Camera`, `GUI` and `DetectionNetwork`, which have been implemented on an asynchronous design on devoted threads. This program grabs an image from a given source (typically a webcam or video or a remote source, using ROS), preprocesses it, and passes it forward an SSD object detection network.

As a result, this program constantly shows the image captured, and the detected objects on the most recent output of the network, yielding the detection score as well. This continuous behavioral can be easily stopped via a couple of buttons on the GUI, making inferences on demand.


[!][Object Detector working](https://github.com/RoboticsLabURJC/2017-tfg-nacho_condes/blob/629b52af73313d39c6a753aae0cacea3d7c4e4ed/docs/Screens/objectdetector_fps.png)

## Getting started
To get this component to work, you will need to install JdeRobot, Python (2.7 for the moment, due to ROS compatibility), and a few Python packages, installable via `python-pip`. See the [Requirements](#requirements) for more details.

Clone this repository, and you are ready to go!

`git clone https://github.com/JdeRobot/dl-objectdetector.git && cd dl-objectdetector`


## Requirements
<p>JdeRobot and ROS are only necessary if you use ROS/ICE video streams. You can run the component with a local webcam/video file (setting up the YML configuration file), with __no need to install ROS__</p>
* JdeRobot ([installation guide](http://jderobot.org/Installation)).
* Python 2.7: `sudo apt install python2`
* Python packages (TensorFlow, Keras, etc.). One-click installing via ``pip``, using the `requirements.txt` file (`pip2 install -r requirements.txt`).
* Protobuf installation: the TensorFlow version of this component relies on `protobufs` to configure model parameters, so the Protobuf libraries must be compiled before using the component ([it's a single command :wink:](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md#protobuf-compilation)).

More dependencies might be installed automatically with the packages mentioned above.
Additionally you might require to install some other dependencies. We have prepared a ```requirements.txt``` file, which you can run using ```pip install -r requirements.txt```

## Installation
This component works on Ubuntu 18.04 and Python 3. In case you want to use inferences from a ROS topic, you will need the Melodic version of ROS, which can be installed [following the official steps](http://wiki.ros.org/melodic/Installation/Ubuntu).

Additionally, you will need some packages which can't be found on the Python repositories, thus they have to be manually installed issuing:
```bash
sudo apt install python3-pyqt5 python3-yaml
```

The remaining required packages have been listed for `pip` to install them automatically:

```bash
pip3 install -r requirements.txt
```
Execute this command using `sudo` if you are not using a virtual environment.

## How to Use
#### For a video stream (ICE/ROS):
Under development.

#### For a local camera/video file (OpenCV):

Just type into the YML configuration file which device/file you want to use, and set the YML node `Source: Local` for a webcam or `Source: Video` for a video file.

---
In another terminal type `python objectdetector.py objectdetector.yml`


This will start the component, driven by the configuration parsed from the YML file (camera endpoint/topic, desired framework, model parameters).

