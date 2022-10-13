import tensorflow as tf
import numpy as np
import glob
import cv2
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
import os
import logging
from deeppress.app_exceptions import ModelNotFound
from deeppress.config import config

logger = logging.getLogger('deeppress.detection')


class DetectorModel:
    def __init__(self):
        self.model_file = None
        self.graph_file = None

        self.detection_graph = None
        self.category_index = None
        self.exported_models_path = config.EXPORTED_MODELS

    def load(self, model):
        if self.model_file != model:
            self.model_file = model
            self.graph_file = "{}.pb".format(model)
            self.detection_graph = None
            self.category_index = None
            self.load_graph()
            self.load_labels()

    def load_labels(self):
        labels_file = "{}.pbtxt".format(self.model_file)
        label_map = label_map_util.load_labelmap(os.path.join(self.exported_models_path, labels_file))
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=100, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)
        print(self.category_index)

    def load_graph(self):
        logger.info("Loading graph %s" % self.graph_file)
        model_path = os.path.join(self.exported_models_path, self.graph_file)
        if not os.path.isfile(model_path):
            raise ModelNotFound(model_path)
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            # Works up to here.
            with tf.io.gfile.GFile(model_path, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
            self.d_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
            self.d_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
            self.d_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
            self.num_d = self.detection_graph.get_tensor_by_name('num_detections:0')

        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.433)
        self.sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options), graph=self.detection_graph)

    def _detect(self, img):
        # Bounding Box Detection.
        with self.detection_graph.as_default():
            # Expand dimension since the model expects image to have shape [1, None, None, 3].
            img_expanded = np.expand_dims(img, axis=0)
            (boxes, scores, classes, num) = self.sess.run(
                [self.d_boxes, self.d_scores, self.d_classes, self.num_d],
                feed_dict={self.image_tensor: img_expanded})
        return boxes, scores, classes, num

    def get_class_name(self, id):
        try:
            return self.category_index[id]['name']
        except:
            return "person"

    def detect(self, img, thresh=0.75):
        # img = cv2.imread(imgpath)
        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        height = img2.shape[0] # Image height
        width = img2.shape[1] # Image width

        # if detector.model_num != netidx:
        #     detector.load_graph('nets/model_{}.pb'.format(netidx), netidx)
        boxes, scores, classes, num = self._detect(img2)

        # thresh = 0.15
        if not thresh:
            thresh = 0.75

        vis_util.visualize_boxes_and_labels_on_image_array(
            img,
            boxes[0],
            classes[0].astype(np.uint8),
            scores[0],
            self.category_index,
            use_normalized_coordinates=True,
            min_score_thresh=thresh,
            line_thickness=8)

        # imgpath = os.path.join("/work", "out_test.jpg")
        # cv2.imwrite(imgpath, img)

        final_boxes = np.squeeze(boxes)
        final_score = np.squeeze(scores)
        final_classes = np.squeeze(classes)

        detected_boxes = []

        for i in range(final_score.shape[0]):
            if scores is None or final_score[i] > thresh:
                ymin, xmin, ymax, xmax = tuple(final_boxes[i].tolist())
                (left, right, top, bottom) = (xmin * width, xmax * width, ymin * height, ymax * height)
                x, y = int(left), int(top)  # Top-Left
                w, h = int(right - left), int(bottom - top)

                detected_boxes.append({
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'acc': int(final_score[i] * 100),
                    'class': self.get_class_name(int(final_classes[i]))
                })

        # logger.debug("Filtering %d detections with %f thresh ==> %d detections" % (final_score.shape[0], thresh, len(detected_boxes)))

        print(detected_boxes)
        return detected_boxes