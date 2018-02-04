# dl-objectdetector
## Note
This is an early release, so it is based on an already downloaded model from TensorFlow, which is working over a SSD detector trained on the COCO (Common Objects in COntext), on 17th November, 2017. In a future release, you will be able to select the desired model, and download it in execution time.
## Requirements
* JdeRobot ([installation guide](http://jderobot.org/Installation)).
* TensorFlow (```sudo pip install tensorflow```).
* [Protobuf installation](https://github.com/tensorflow/models/tree/master/research/object_detection) (read below).

More dependencies might be installed automatically with the packages mentioned above.

## Basement
This component works over a library of TensorFlow pre-trained models, importing one of them and embedding it on the component developed [here](https://github.com/RoboticsURJC-students/2017-tfg-nacho_condes). Hence, to be able to run it, we have to install previously the ```protobufs``` provided with the models, following the installation guide.

## Behavioral
For the moment, this node handles a real-time stream of video (incoming by an ICE/ROS proxy, automatically processed by the `comm` library), and shows a window displaying it, and also the output from the detection network. It provides a button for toggling on/off the real-time detection (TODO: implement another button to process a single frame on demand)
