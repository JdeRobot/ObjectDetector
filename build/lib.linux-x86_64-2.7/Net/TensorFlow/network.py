import tensorflow as tf
import numpy as np
import tarfile
import os

from Net.utils import label_map_util

LABELS_DICT = {'voc': 'Net/labels/pascal_label_map.pbtxt',
               'coco': 'Net/labels/mscoco_label_map.pbtxt',
               'kitti': 'Net/labels/kitti_label_map.txt',
               'oid': 'Net/labels/oid_bboc_trainable_label_map.pbtxt',
               'pet': 'Net/labels/pet_label_map.pbtxt'}

class DetectionNetwork():
    def __init__(self, net_model):
        self.framework = "TensorFlow"

        labels_file = LABELS_DICT[net_model['Dataset'].lower()]
        label_map = label_map_util.load_labelmap(labels_file) # loads the labels map.
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes= 999999)
        category_index = label_map_util.create_category_index(categories)
        self.classes = {}
        # We build is as a dict because of gaps on the labels definitions
        for cat in category_index:
            self.classes[cat] = str(category_index[cat]['name'])

        # Frozen inference graph, written on the file
        CKPT = 'Net/TensorFlow/' + net_model['Model']
        detection_graph = tf.Graph() # new graph instance.
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        # Set additional parameters for the TF session
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.8)
        config = tf.ConfigProto(gpu_options=gpu_options,
                                log_device_placement=False)
        self.sess = tf.Session(graph=detection_graph, config=config)
        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        # NCHW conversion. not possible
        #self.image_tensor = tf.transpose(self.image_tensor, [0, 3, 1, 2])
        self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        self.boxes = []
        self.scores = []
        self.predictions = []


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
