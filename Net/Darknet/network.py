import darknet
import numpy as np
from PIL import Image

from Net.utils import label_map_util

LABELS_DICT = {'voc': 'Net/labels/pascal_label_map.pbtxt',
               'coco': 'Net/labels/mscoco_label_map.pbtxt',
               'kitti': 'Net/labels/kitti_label_map.txt',
               'oid': 'Net/labels/oid_bboc_trainable_label_map.pbtxt',
               'pet': 'Net/labels/pet_label_map.pbtxt'}

class DetectionNetwork():
    def __init__(self, net_model):
        self.framework = "Darknet"

        # Parse the dataset to get which labels to yield
        # TODO: we should hand them over to Darknet to avoid duplication
        # TODO: (or read them from the Darknet data file)
        labels_file = LABELS_DICT[net_model['Dataset'].lower()]
        label_map = label_map_util.load_labelmap(labels_file) # loads the labels map.
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=100000)
        category_index = label_map_util.create_category_index(categories)
        self.classes = {}
        # We build is as a dict because of gaps on the labels definitions
        for cat in category_index:
            self.classes[cat] = str(category_index[cat]['name'])

        WEIGHTS_FILE = 'Net/Darknet/' + net_model['Model'] + '.weights'
        CONFIG_FILE = 'Net/Darknet/' + net_model['Model'] + '.cfg'
        LABELS_FILE = 'Net/Darknet/coco.data'           # Hardcoded for now!

        self.model = darknet.load_net(CONFIG_FILE, WEIGHTS_FILE, 0)
        self.meta = darknet.load_meta(LABELS_FILE)

        # Output preallocation
        self.predictions = np.asarray([])
        self.boxes = np.asarray([])
        self.scores = np.asarray([])

        print("Network ready!")


    def setCamera(self, cam):
        self.cam = cam

        self.original_height = cam.im_height
        self.original_width = cam.im_width

        # Factors to rescale the output bounding boxes
        # self.height_factor = np.true_divide(self.original_height, self.img_height)
        # self.width_factor = np.true_divide(self.original_width, self.img_width)

        # No scaling, for now
        self.height_factor = 1
        self.width_factor = 1

    def predict(self):
        input_image = self.cam.getImage()

        predictions = darknet.detect_from_image(self.model, self.meta, input_image)
        print(predictions)

        self.predictions = []
        self.scores = []
        self.boxes = []

        # iterate over predictions
        for prediction in predictions:
            self.predictions.append(prediction[0])
            self.scores.append(prediction[1])

            # No scaling for now
            box = prediction[2]
            box_x = box[0]
            box_y = box[1]
            box_w = box[2]
            box_h = box[3]
            xmin = int((box_x - box_w / 2) * self.width_factor)
            ymin = int((box_y - box_h / 2) * self.height_factor)
            xmax = xmin + int(box_w * self.width_factor)
            ymax = ymin + int(box_h * self.height_factor)
            self.boxes.append([xmin, ymin, xmax, ymax])
