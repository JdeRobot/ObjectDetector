# dl-objectdetector (TensorFlow + Keras)

### Contents

1. [Introduction](#introduction)
2. [Getting started](#getting-started)
3. [Requirements](#requirements)
4. [How to use](#how-to-use)
5. [Framework choice](#framework-choice)
## Introduction

`dl-objectdetector` is a JdeRobot node, composed of 3 entities: `Camera`, `GUI` and `DetectionNetwork`, which have been implemented on an asynchronous design with its own thread. As a result, we have an easily window which simultaneously shows on real-time the image captured from a webcam or video (via OpenCV) or remote proxy (through a ROS/ICE communicator, coming from the JdeRobot suite), and the same image with _bounding boxes_ on it, surrounding the objects which the TF/Keras Neural Network has detected on it (yielding the detection score as well). Also, this continuous video detection flow can be easily stopped via a couple of buttons on the GUI, and turn the component to do on-demand detection.

This has been developed on a way which allows the Neural Network to be implemented as a Python class (`DetectionNetwork()`), which can be extracted from the component and used to load and use any kind of model, and even handle real-time and on-demand detection, via the thread (`ThreadNetwork()`). This can have really useful applications, some of which will be developed soon!

<center>

<img src="https://roboticsurjc-students.github.io/2017-tfg-nacho_condes/Screens/objectdetector_fps.png">Object Detector working</img>
</center>

## Getting started
To get this component to work, you will need to install JdeRobot, Python (2.7 for the moment, due to ROS compatibility), and a few Python packages, installable via `python-pip`. See the [Requirements](#requirements) for more details.

It is also tested on Python 3.5.2, due to compatibility with PyQt5, and it works fine.

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


## How to Use
#### For a video stream (ICE/ROS):
Open a terminal and type `camserver camserver.cfg`. This will start the `camserver` (old `cameraserver`) component, which will serve a specified video or the webcam image through an ICE proxy. You can learn more about this JdeRobot component [here](https://jderobot.org/Handbook#Cameraserver). Besides, you are able to create a ROS topic (with a driver) and process the images incoming from a drone: the implemented `comm` library can also handle this.

You will have to specify this in the YML configuration file, and set the YML node `Source: Stream`

#### For a local camera/video file (OpenCV):

Just type into the YML configuration file which device/file you want to use, and set the YML node `Source: Local` for a webcam or `Source: Video` for a video file.

---
In another terminal type `python2 objectdetector.py objectdetector.yml`


This will start the component, driven by the configuration parsed from the YML file (camera endpoint/topic, desired framework, model parameters).
## Framework choice
The <code>objectdetector.yml</code> configuration file allows you to choose which of the available frameworks (Keras, TensorFlow) you want to deploy on the component (you can discover which one is selected on a running instance on the window title).

Also, you will have to specify the model which you want to load. There is a model already included for each framework (extract the <code>model.zip</code> present on the Net/{TensorFlow, Keras} directory). The field <code>Network.Model</code> on the YML file musts contain the filename for the model:

* TensorFlow: It requires a <code>.pb</code> file, which contains a frozen instance of a <code>tf.Graph</code> structure (neural units weights included). A lot of models are included on the [TensorFlow model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md), available for download (choose those which output _boxes_. We have succesfully tried SSD and RCNN detectors). As said, you will have to extract the <code>.pb</code> file from the <code>.tar.gz</code> downloaded file on the Net/TensorFlow directory, and then specify the filename on the YML file.

* Keras: It requires a <code>.h5</code> file, which can contain the full model saved, or only the weights of the neural units. You can load it anyway! The file provided by us contains a full model, but you can load the detector you prefer from [this set](https://github.com/pierluigiferrari/ssd_keras#download-the-original-trained-model-weights). If it contains weights, please ensure that it belongs to a SSD 300x300 or SSD 512x512 network, as those are the only supported structures for now.

No matter which framework you choose, you will also have to specify on the YML config file which was the dataset on which the model was trained (because of label issues. The pure network yields an integer label, which has to be mapped into a class name. This correspondence varies across the datasets).

Nothing else is necessary, __rock it!__
