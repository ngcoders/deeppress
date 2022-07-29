import sys
import cv2
# import tensorflow as tf
import random
import json
import logging
import os
from datetime import datetime
import shutil

from object_detection.utils import dataset_util
from object_detection.utils import label_map_util


_LOGGER = logging.getLogger('deeppress.image_to_tfr')


class TFRConverter:
    """
    Class to convert image to TF records
    """

    def __init__(self, file_name, labels_file=False):
        time_str = datetime.now().strftime('%y%m%d_%H%M%S')
        if not os.path.isdir(file_name):
            os.mkdir(file_name)
        self.data_dir = file_name
        self.train_set = f'{file_name}/train_baheads.tfrecord-{time_str}'
        self.test_set = f'{file_name}/test_baheads.tfrecord-{time_str}'
        self.stats_file = f'{file_name}/stats.json'
        self.train_count = 0
        self.test_count = 0

        # Load labels
        labels_file = labels_file
        label_map = label_map_util.load_labelmap(labels_file)
        self.categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=100, use_display_name=False)
        print(self.categories)
        try:
            with open(self.stats_file) as _f:
                self.counts = json.load(_f)
        except:
            self.counts = {'train': 0, 'test': 0, 'classes': len(self.categories)}

    def __enter__(self):
        import tensorflow as tf
        self.train_writer = tf.io.TFRecordWriter(self.train_set)
        self.test_writer = tf.io.TFRecordWriter(self.test_set)
        return self

    def __exit__(self, *args):
        self.train_writer.close()
        self.test_writer.close()
        try:
            self.counts['classes'] = len(self.categories)
            with open(self.stats_file, 'w') as _f:
                json.dump(self.counts, _f)
        except Exception as e:
            _LOGGER.error(e)
        if self.test_count == 0:
            os.remove(self.test_set)
        if self.train_count == 0:
            os.remove(self.train_set)

    def add_record(self, filename, boxes):
        """
        Add a new record to train-test dataset

        :param filename: Image file path
        :param boxes: Boxes
        :return: None
        """

        tf_example = self.create_tf_example(filename, boxes)
        if tf_example is None:
            return

        if random.random() > 0.2:
            self.train_writer.write(tf_example.SerializeToString())
            self.counts['train'] += 1
            self.train_count += 1
        else:
            self.test_writer.write(tf_example.SerializeToString())
            self.counts['test'] += 1
            self.test_count += 1

    def clean(self):
        # os.remove(self.train_set)
        # os.remove(self.test_set)
        shutil.rmtree(self.data_dir)
        os.remove(self.stats_file)

    def get_class_id(self, name):
        """Get the class id for name"""
        person_id = 1
        for cat in self.categories:
            if cat['name'] == name:
                return name, cat['id']
            if cat['name'] == 'person':
                person_id = cat['id']

        return 'person', person_id

    def create_tf_example(self, filename, boxes):
        import tensorflow as tf
        img = cv2.imread(filename)
        if img is None:
            return None

        height = img.shape[0] # Image height
        width = img.shape[1] # Image width
        # Filename of the image. Empty if image is not from file
        _, encoded_image_data = cv2.imencode(".jpg", img) # Encoded image bytes

        image_format = b'jpeg'  # or b'png'

        xmins = []  # List of normalized left x coordinates in bounding box (1 per box)
        xmaxs = []  # List of normalized right x coordinates in bounding box (1 per box)
        ymins = []  # List of normalized top y coordinates in bounding box (1 per box)
        ymaxs = []  # List of normalized bottom y coordinates in bounding box (1 per box)
        classes_text = []  # List of string class name of bounding box (1 per box)
        classes = []  # List of integer class id of bounding box (1 per box)

        for box in boxes:
            xmin = box['x']
            box_w = box['width']
            ymin = box['y']
            box_h = box['height']

            xmin, box_w, ymin, box_h = map(float,[xmin, box_w, ymin, box_h])
            xmax = (xmin + box_w)/width
            xmin /= width
            ymax = (ymin + box_h)/height
            ymin /= height


            xmins.append(xmin)
            xmaxs.append(xmax)
            ymins.append(ymin)
            ymaxs.append(ymax)

            object_class = 'person'
            if 'class' in box.keys():
                object_class = box['class']

            object_class, _id = self.get_class_id(object_class)
            classes.append(_id)
            classes_text.append(str.encode(object_class))

        tf_example = tf.train.Example(features=tf.train.Features(feature={
            'image/height': dataset_util.int64_feature(height),
            'image/width': dataset_util.int64_feature(width),
            'image/filename': dataset_util.bytes_feature(filename.encode()),
            'image/source_id': dataset_util.bytes_feature(filename.encode()),
            'image/encoded': dataset_util.bytes_feature(encoded_image_data.tobytes()),
            'image/format': dataset_util.bytes_feature(image_format),
            'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
            'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
            'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
            'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
            'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
            'image/object/class/label': dataset_util.int64_list_feature(classes),
        }))
        return tf_example