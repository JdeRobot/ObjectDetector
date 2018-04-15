import tensorflow as tf
import numpy as np
import tarfile
import os

from utils import label_map_util

class DetectionNetwork():
    ''' Class to create a tensorflow network, based on SSD detection trained on COCO dataset
    (for the moment). At its creation, it imports the weight from the frozen model.'''
    def __init__(self, net_model):
        self.framework = "TensorFlow"
        try:
            # path to the downloaded model.
            MODEL_NAME = 'Net/TensorFlow/' + net_model['MODEL_NAME']
            # the class is called from the root dir of the project!
            MODEL_FILE = MODEL_NAME + '.tar.gz'

            # Frozen graph (inside the model).
            CKPT = net_model['CKPT']

            # Reference to the file containing the relationship between labels and ids
            LABELS = net_model['LABELS']

            NUM_CLASSES = net_model['NUM_CLASSES']

        except:
            raise SystemExit('Incorrect or incomplete model details in YML file')


        # analysing the .tar model.
        tar_file = tarfile.open(MODEL_FILE)
        for file in tar_file.getmembers(): # checking if frozen graph exists.
            file_name = os.path.basename(file.name)
            if 'frozen_inference_graph.pb' in file_name:
                tar_file.extract(file, os.getcwd() + '/Net/TensorFlow') # extract everything.

        detection_graph = tf.Graph() # new graph instance.
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile((MODEL_NAME + '/' + CKPT), 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        label_map = label_map_util.load_labelmap(('Net/TensorFlow/labels/' + LABELS)) # loads the labels map.
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES)
        category_index = label_map_util.create_category_index(categories)
        self.classes = {}
        # We build is as a dict because of gaps on the labels definitions
        for cat in category_index:
            self.classes[cat] = str(category_index[cat]['name'])

        self.sess = tf.Session(graph=detection_graph)
        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        # NCHW conversion. not possible
        #self.image_tensor = tf.transpose(self.image_tensor, [0, 3, 1, 2])
        self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')


        # Dummy initialization (otherwise it takes longer then)
        dummy_tensor = np.zeros((1,1,1,3), dtype=np.int32)
        self.sess.run(
                [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
                feed_dict={self.image_tensor: dummy_tensor})

        self.confidence_threshold = 0.5

        print("Network ready!")

    def setCamera(self, cam):
        self.cam = cam
        self.original_height = cam.im_height
        self.original_width = cam.im_width


    def predict(self):
        input_image = self.cam.getImage()
        image_np_expanded = np.expand_dims(input_image, axis=0)
        (boxes, scores, predictions, _) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})

        # We only keep the most confident predictions.
        conf = scores > self.confidence_threshold # bool array
        boxes = boxes[conf]
        # aux variable for avoiding race condition while int casting
        tmp_boxes = np.zeros([len(boxes), 4])
        tmp_boxes[:,[0,2]] = boxes[:,[1,3]] * self.original_width
        tmp_boxes[:,[3,1]] = boxes[:,[2,0]] * self.original_height
        self.boxes = tmp_boxes.astype(int)

        self.scores = scores[conf]
        predictions = predictions[conf].astype(int)
        self.predictions = []
        for pred in predictions:
            self.predictions.append(self.classes[pred])
