from deeppress.detection import DetectorModel
import cv2
import numpy

class DeepPressApp(object):
    def __init__(self):
        self.training_job = None
        self.detector = DetectorModel()
        self.mode_file = None

    def is_training(self):
        return False

    def current_model(self):
        return self.mode_file

    def load_model(self, model_file):
        self.detector.load(model_file)

    def detect(self, image_data, thresh):
        img = cv2.imdecode(numpy.fromstring(image_data, numpy.uint8), cv2.IMREAD_UNCHANGED)
        return self.detector.detect(img, thresh)

    def start_training(self, job):
        pass