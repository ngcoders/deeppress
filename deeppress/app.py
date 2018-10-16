from deeppress.detection import DetectorModel
from deeppress.trainer import TrainingApp
import cv2
import numpy

class DeepPressApp(object):
    def __init__(self):
        self.training_job = None
        self.detector = DetectorModel()
        self.mode_file = None
        self.trainer = TrainingApp()

    def is_training(self):
        return self.trainer.current_job and self.trainer.current_job.is_alive()

    def start_training(self):
        if self.trainer:
            self.trainer.start()

    def stop_training(self):
        if self.trainer:
            self.trainer.stop()

    def get_training_status(self):
        return self.trainer.status()

    def current_model(self):
        return self.mode_file

    def load_model(self, model_file):
        self.detector.load(model_file)

    def detect(self, image_data, thresh):
        img = cv2.imdecode(numpy.fromstring(image_data, numpy.uint8), cv2.IMREAD_UNCHANGED)
        return self.detector.detect(img, thresh)
