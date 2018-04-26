from keras import backend as K
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
from PIL import Image
import h5py

from keras_loss_function.keras_ssd_loss import SSDLoss
from keras_layers.keras_layer_AnchorBoxes import AnchorBoxes
from keras_layers.keras_layer_DecodeDetections import DecodeDetections
from keras_layers.keras_layer_L2Normalization import L2Normalization
from Net.utils import label_map_util, create_model_from_weights



LABELS_DICT = {'voc': 'Net/labels/pascal_label_map.pbtxt',
               'coco': 'Net/labels/mscoco_label_map.pbtxt',
               'kitti': 'Net/labels/kitti_label_map.txt',
               'oid': 'Net/labels/oid_bboc_trainable_label_map.pbtxt',
               'pet': 'Net/labels/pet_label_map.pbtxt'}



class DetectionNetwork():
    def __init__(self, net_model):
        self.framework = "Keras"
        # Parse the dataset to get which labels to yield
        labels_file = LABELS_DICT[net_model['Dataset'].lower()]
        label_map = label_map_util.load_labelmap(labels_file) # loads the labels map.
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=100000)
        category_index = label_map_util.create_category_index(categories)
        self.classes = {}
        # We build is as a dict because of gaps on the labels definitions
        for cat in category_index:
            self.classes[cat] = str(category_index[cat]['name'])

        MODEL_FILE = 'Net/Keras/' + net_model['Model']

        file = h5py.File(MODEL_FILE, 'r')


        ssd_loss = SSDLoss(neg_pos_ratio=3, n_neg_min=0, alpha=1.0)

        K.clear_session()

        if str(file.items()[0][0]) == 'model_weights':
            print("Full model detected. Loading it...")
            try:
                self.model = load_model(MODEL_FILE, custom_objects={'AnchorBoxes': AnchorBoxes,
                                                               'L2Normalization': L2Normalization,
                                                               'DecodeDetections': DecodeDetections,
                                                               'compute_loss': ssd_loss.compute_loss})
            except Exception as e:
                SystemExit(e)
        else:
            print("Weights file detected. Creating a model and loading the weights into it...")
            print "Model file: ", MODEL_FILE
            self.model = create_model_from_weights.create_model(MODEL_FILE,
                                                                ssd_loss,
                                                                len(self.classes))



        # the Keras network works on 300x300 images. Reference sizes:
        input_size = self.model.input.shape.as_list()
        self.img_height = input_size[1]
        self.img_width = input_size[2]


        # Output preallocation
        self.predictions = np.asarray([])
        self.boxes = np.asarray([])
        self.scores = np.asarray([])

        dummy = np.zeros([1, self.img_height, self.img_width, 3])
        self.model.predict(dummy)

        print("Network ready!")


    def setCamera(self, cam):
        self.cam = cam

        self.original_height = cam.im_height
        self.original_width = cam.im_width

        # Factors to rescale the output bounding boxes
        self.height_factor = np.true_divide(self.original_height, self.img_height)
        self.width_factor = np.true_divide(self.original_width, self.img_width)


    def predict(self):
        input_image = self.cam.getImage()
        # preprocessing
        as_image = Image.fromarray(input_image)
        resized = as_image.resize((self.img_width,self.img_height), Image.NEAREST)
        np_resized = image.img_to_array(resized)

        input_col = []
        input_col.append(np_resized)
        network_input = np.array(input_col)
        # Prediction
        y_pred = self.model.predict(network_input)

        self.predictions = []
        self.scores = []
        self.boxes = []
        confidence_threshold = 0.5
        # which predictions are above the confidence threshold?
        y_pred_thresh = [y_pred[k][y_pred[k,:,1] > confidence_threshold] for k in range(y_pred.shape[0])]
        # iterate over them
        for box in y_pred_thresh[0]:
            self.predictions.append(self.classes[int(box[0])])
            self.scores.append(box[1])
            xmin = int(box[2] * self.width_factor)
            ymin = int(box[3] * self.height_factor)
            xmax = int(box[4] * self.width_factor)
            ymax = int(box[5] * self.height_factor)
            self.boxes.append([xmin, ymin, xmax, ymax])
