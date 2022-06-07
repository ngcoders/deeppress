
import os
import cv2
import math
import time
import glob
import logging
from time import time
from functools import wraps
import tensorflow as tf
import numpy as np
import pandas as pd
from PIL import Image
from google.protobuf import text_format
from object_detection.protos import string_int_label_map_pb2

gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
debug_time = True
_LOGGER = logging.getLogger('deeppress.tf2_detector')


def timing(func):
    @wraps(func)
    def wrap(*args, **kw):
        ts = time()
        result = func(*args, **kw)
        te = time()
        if debug_time:
            _LOGGER.debug(f'{func.__name__}() took {te-ts:2.6f}s')
        return result
    return wrap


class TF2DetectorModel():
    def __init__(self):
        self.model = None
        self.modelname = None
        self.model_file = None
        self.labels = None
    
    def load(self, path, modelname):
        if modelname != self.modelname:
            # load the model if it is not loaded before
            self.load_model(path, modelname)
            self.load_labels(path, modelname)
            self.modelname = modelname
        return
    
    def unload(self):
        if self.modelname is not None:
            # unload the model to free up GPU space
            _LOGGER.debug(f'Unloading {self.modelname}')
            del self.model
            del self.modelname
            del self.model_file
            del self.labels
            self.model = None
            self.modelname = None
            self.model_file = None
            self.labels = None
        return

    @timing
    def load_model(self, path, modelname):
        if not os.path.exists(os.path.join(path, modelname, 'saved_model')):
            raise FileNotFoundError(f'Model {modelname} not found')
        saved_model = tf.saved_model.load(os.path.join(path, modelname, 'saved_model'))
        # model = saved_model.signatures['serving_default']
        # print(saved_model.signatures)
        # print(list(saved_model.signatures.keys()))  # ["serving_default"]
        # print(model.inputs)
        # print(model.outputs)
        # print(model.structured_outputs)
        self.model = saved_model
        return

    @timing
    def load_labels(self, path, modelname):
        # try to get the modelname.pbtxt file
        labels_file = os.path.join(path, modelname, 'saved_model', 'saved_model.pbtxt')
        if not os.path.exists(labels_file):
            # if not found, look for baheads_map.pbtxt
            labels_file = os.path.join(path, 'baheads_map.pbtxt')
        if not os.path.exists(labels_file):
            raise FileNotFoundError('Labels file does not exist')
        with open(labels_file, 'r') as labels_file:
            labels_string = labels_file.read()
            labels_map = string_int_label_map_pb2.StringIntLabelMap()
            try:
                text_format.Merge(labels_string, labels_map)
            except text_format.ParseError:
                labels_map.ParseFromString(labels_string)
            labels_dict = {item.id: item.display_name for item in labels_map.item}
        self.labels = labels_dict
        return

    @timing
    def detect(self, image, thresh=75):
        image = np.asarray(image)
        height = image.shape[0] # Image height
        width = image.shape[1] # Image width
        input_tensor = tf.convert_to_tensor(image)
        # adding one more dimension since model expect a batch of images.
        input_tensor = input_tensor[tf.newaxis, ...]
        # run the detection
        output_dict = self.model(input_tensor)
        num_detections = int(output_dict.pop('num_detections'))
        output_dict = {
            key: value[0, :num_detections].numpy()
            for key, value in output_dict.items()
            # if key != 'num_detections'
        }
        output_dict = self.filter(output_dict, thresh, height, width)
        self.draw_boxes_on_input_image(image, output_dict, thresh)

        return output_dict
    
    def filter(self, boxes, thresh, height, width):
        output = []
        for index in range(len(boxes)):
            if boxes['detection_scores'][index] > thresh / 100:
                ymin, xmin, ymax, xmax = tuple(boxes['detection_boxes'][index].tolist())
                (left, right, top, bottom) = (xmin * width, xmax * width, ymin * height, ymax * height)
                x, y = int(left), int(top)  # Top-Left
                w, h = int(right - left), int(bottom - top)
                classId = int(boxes['detection_classes'][index])
                box = {
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'acc': int(boxes['detection_scores'][index] * 100),
                    'classId': classId,
                    'class': self.labels[classId],
                }
                output += [box]
        return output

    @timing
    def draw_true_boxes_on_image(self, image, detections):
        '''
        this is used to draw the true boxes on the image
        '''
        image_with_detections = image
        width, height, channels = image_with_detections.shape
        color = (255, 255, 0)

        num_detections = detections['num_detections']
        if num_detections > 0:
            for detection_index in range(num_detections):
                detection_score = detections['detection_scores'][detection_index]
                detection_box = detections['detection_boxes'][detection_index]
                detection_class = detections['detection_classes'][detection_index]
                detection_label = self.labels[detection_class]
                detection_label_full = detection_label + ' ' + str(math.floor(100 * detection_score)) + '%'

                y1 = int(width * detection_box[0])
                x1 = int(height * detection_box[1])
                y2 = int(width * detection_box[2])
                x2 = int(height * detection_box[3])

                # Detection rectangle.    
                image_with_detections = cv2.rectangle(
                    image_with_detections,
                    (x1, y1),
                    (x2, y2),
                    color,
                    3
                )
        return image_with_detections

    # @timing
    def draw_detections_on_image(self, image, detections, thresh=30):
        '''
        this is a modified version of the original detector.
        Please find the original in the pal_detector repo.
        '''
        image_with_detections = image
        width, height, channels = image_with_detections.shape

        font = cv2.FONT_HERSHEY_SIMPLEX
        color = (0, 255, 0)
        label_padding = 5

        # num_detections = len(detections)
        # if num_detections > 0:
        for detection in detections:
            detection_score = detection['acc']
            if detection_score < thresh:
                continue
            # detection_box = detection['detection_boxes']
            # detection_class = detection['classId']
            detection_label = detection['class']
            detection_label_full = detection_label + ' ' + str(math.floor(detection_score)) + '%'

            y1 = int(detection['y'])
            x1 = int(detection['x'])
            y2 = int(y1 + detection['width'])
            x2 = int(x1 + detection['height'])

            # Detection rectangle.    
            image_with_detections = cv2.rectangle(
                image_with_detections,
                (x1, y1),
                (x2, y2),
                color,
                3
            )

            # Label background.
            label_size = cv2.getTextSize(
                detection_label_full,
                cv2.FONT_HERSHEY_COMPLEX,
                0.7,
                2
            )
            image_with_detections = cv2.rectangle(
                image_with_detections,
                (x1, y1 - label_size[0][1] - 2 * label_padding),
                (x1 + label_size[0][0] + 2 * label_padding, y1),
                color,
                -1
            )

            # Label text.
            cv2.putText(
                image_with_detections,
                detection_label_full,
                (x1 + label_padding, y1 - label_padding),
                font,
                0.7,
                (0, 0, 0),
                1,
                cv2.LINE_AA
            )
        return image_with_detections

    def save_image(self, image_with_detections_np, filename):
        image_with_detections = Image.fromarray(image_with_detections_np)
        # filename = filename.rsplit(".", 1)[0] + '_detections.jpg'
        filename = '_tf2_' + filename
        image_with_detections.save(filename)

    def draw_boxes_on_input_image(self, image_np, detections, thresh=30):
        ''' draw detection boxes on the received image and save it '''
        self.save_image(image_np, 'received_image.jpg')
        image_with_detections_np = self.draw_detections_on_image(image_np, detections, thresh)
        self.save_image(image_with_detections_np, 'received_image_boxes.jpg')

    def detect_and_save_image(self, path_sample_image):
        with Image.open(path_sample_image) as image:
            image_np = np.array(image)
            if len(image_np.shape) == 2:
                # to convert a grayscale to 3-channel image
                image_np = np.stack((image_np,)*3, axis=-1)
            detections = self.detect(image_np, thresh = 0.6)
            print(f'detections: {detections}')
            image_with_detections_np = self.draw_detections_on_image(image_np, detections)
            self.save_image(image_with_detections_np, path_sample_image)

    def get_true_boxes_from_csv(self, data_csv, filename):
        filename = filename.rsplit("/")[-1]
        filtered = data_csv[data_csv['filename'].str.contains(filename)]
        filtered = filtered.reset_index(drop=True)
        num_detections = len(filter)
        detections = {
            'num_detections': num_detections,
            'detection_classes': [],
            'detection_scores': [],
            'detection_boxes': []
        }
        for i in range(num_detections):
            detections['detection_classes'].append(1)
            detections['detection_scores'].append(100)
            #print(filter['width'][0])
            detection_box = [
                filtered['ymin'][i]/filtered['height'][0],
                filtered['xmin'][i]/filtered['width'][0],
                filtered['ymax'][i]/filtered['height'][0],
                filtered['xmax'][i]/filtered['width'][0]
            ]
            detections['detection_boxes'].append(detection_box)
        return detections

    def detect_images_from_folder(self, path_folder):
        if(os.path.exists(path_folder) is False):
            print('Error: Folder does not exist')
            return
        output_folder_path = '_tf_' + path_folder
        if(os.path.exists(output_folder_path) is False):
            os.mkdir(output_folder_path)
        filename_csv = sorted(glob.glob(path_folder + '/*.csv'))
        if(len(filename_csv) == 0):
            print('Skipping true boxes')
            data_csv = pd.DataFrame()
        else:
            print('Including true boxes')
            data_csv = pd.read_csv(filename_csv[0])

        for filename in sorted(glob.glob(path_folder + '/*.jpg')):
            with Image.open(filename) as image:
                image_np = np.array(image)
                if len(image_np.shape) == 2:   # to convert a grayscale to 3-channel image
                    image_np = np.stack((image_np,)*3, axis=-1)
                detections = self.detect(image_np)
                if not data_csv.empty:
                    true_boxes = self.get_true_boxes_from_csv(data_csv, filename)
                    image_np = self.draw_true_boxes_on_image(image_np, true_boxes)
                image_with_detections_np = self.draw_detections_on_image(image_np, detections)
                image_with_detections = Image.fromarray(image_with_detections_np)
                image_with_detections.save('_tf_' + filename)
