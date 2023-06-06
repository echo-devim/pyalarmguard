from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import config
import os

class ObjectDetection:

	def __init__(self,logger):
		prototxt = "detectors/objdetection/MobileNetSSD_deploy.prototxt.txt"
		model = "detectors/objdetection/MobileNetSSD_deploy.caffemodel"
		self.confidence = 0.4 # threshold
		# initialize the list of class labels MobileNet SSD was trained to
		# detect, then generate a set of bounding box colors for each class
		self.CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
			"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
			"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
			"sofa", "train", "tvmonitor"]
		self.COLORS = np.random.uniform(0, 255, size=(len(self.CLASSES), 3))

		# load our serialized model from disk
		logger.info("loading model for object detection")
		self.net = cv2.dnn.readNetFromCaffe(prototxt, model)


	def detect(self, imagepath):
		objects = []
		if not os.path.exists(imagepath):
			return objects
		
		image = cv2.imread(imagepath)

		# grab the frame dimensions and convert it to a blob
		#(h, w) = image.shape[:2]
		blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)),
		0.007843, (300, 300), 127.5)

		# pass the blob through the network and obtain the detections and
		# predictions
		self.net.setInput(blob)
		detections = self.net.forward()

		# loop over the detections
		for i in np.arange(0, detections.shape[2]):
			# extract the confidence (i.e., probability) associated with
			# the prediction
			confidence = detections[0, 0, i, 2]

			# filter out weak detections by ensuring the `confidence` is
			# greater than the minimum confidence
			if confidence > self.confidence:
				# extract the index of the class label from the
				# `detections`, then compute the (x, y)-coordinates of
				# the bounding box for the object
				idx = int(detections[0, 0, i, 1])
				#box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
				#(startX, startY, endX, endY) = box.astype("int")

				objects.append({"label":self.CLASSES[idx], "confidence":confidence})

				# draw the prediction on the frame
				#label = "{}: {:.2f}%".format(self.CLASSES[idx],
				#	confidence * 100)
				#cv2.rectangle(image, (startX, startY), (endX, endY),
				#	self.COLORS[idx], 2)
				#y = startY - 15 if startY - 15 > 15 else startY + 15
				#cv2.putText(image, label, (startX, y),
				#	cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS[idx], 2)

		# write the output frame
		#cv2.imwrite(imagepath, image)

		return objects
