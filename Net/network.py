import tensorflow as tf
import numpy as np
import six.moves.urllib as urllib
import sys
import tarfile
import zipfile
import os
import time
import threading

from utils import label_map_util

from utils import visualization_utils as vis_util

import cv2


class Detection_Network():
	''' Class to create a tensorflow network, based on SSD detection trained on COCO dataset
	(for the moment). At its creation, it imports the weight from the frozen model.'''
	def __init__(self):
		# path to the downloaded model.
		MODEL_NAME = 'Net/' + 'ssd_mobilenet_v1_coco_2017_11_17'
		# the class is called from the root dir of the project!
		MODEL_FILE = MODEL_NAME + '.tar.gz'

		# path to the frozen graph (inside the model).
		PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

		# path to the labels (id-name association).
		PATH_TO_LABELS = os.path.join('Net/data', 'mscoco_label_map.pbtxt')

		NUM_CLASSES = 90
		# analysing the .tar model.
		tar_file = tarfile.open(MODEL_FILE)
		for file in tar_file.getmembers(): # checking if frozen graph exists.
			file_name = os.path.basename(file.name)
			if 'frozen_inference_graph.pb' in file_name:
				tar_file.extract(file, os.getcwd() + '/Camera/network') # extract everything.

		detection_graph = tf.Graph() # new graph instance.
		with detection_graph.as_default():
			od_graph_def = tf.GraphDef()
			with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
				serialized_graph = fid.read()
				od_graph_def.ParseFromString(serialized_graph)
				tf.import_graph_def(od_graph_def, name='')

		label_map = label_map_util.load_labelmap(PATH_TO_LABELS) # loads the labels map.
		categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES)
		self.category_index = label_map_util.create_category_index(categories)

		self.sess = tf.Session(graph=detection_graph)
		self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
		self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
		self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
		self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
		self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

		print("Network created!")

		self.lock = threading.Lock()

		# tensor for initializing the network
		# (otherwise it takes a little to get the first
		# prediction)
		dummy_tensor = np.zeros((1,1,1,3), dtype=np.int32)
		self.sess.run(
				[self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
				feed_dict={self.image_tensor: dummy_tensor})

		self.input_image = None
		self.output_image = None


	def predict(self):
		image_np = self.input_image
		if image_np is not None:
			image_np.setflags(write=1)
			image_np_expanded = np.expand_dims(image_np, axis=0)
			(boxes, scores, classes, num) = self.sess.run(
				[self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
				feed_dict={self.image_tensor: image_np_expanded})
			# visualization of the results.
			vis_util.visualize_boxes_and_labels_on_image_array(
				image_np,
				np.squeeze(boxes),
				np.squeeze(classes).astype(np.int32),
				np.squeeze(scores),
				self.category_index,
				use_normalized_coordinates=True,
				line_thickness=6)
		else:
			image_np = np.zeros((360, 240), dtype=np.int32)

		return image_np

	def update(self):
		self.lock.acquire()
		self.output_image = self.predict()
		self.lock.release()
