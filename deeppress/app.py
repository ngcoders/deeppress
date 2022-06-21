from multiprocessing import Process
from deeppress.tf2_detection import TF2DetectorModel as DetectorModel
from deeppress.trainer import TrainingApp
import cv2
import numpy
from deeppress.config import config

class DeepPressApp(Process):
    def __init__(self):
        super(Process, self).__init__()
        self.running = True
        self.training_job = None
        self.detector = DetectorModel()
        self.mode_file = None
        self.trainer = TrainingApp()

    def is_training(self):
        return self.trainer.current_job and self.trainer.current_job.is_alive()

    def start_training(self):
        if self.trainer:
            self.unload_model()
            self.trainer.start()

    def stop_training(self):
        if self.trainer:
            self.trainer.stop()

    def get_training_status(self):
        return self.trainer.status()

    def current_model(self):
        return self.mode_file

    def load_model(self, model):
        self.detector.load(config.EXPORTED_MODELS, model)

    def unload_model(self):
        self.detector.unload()

    def detect(self, image_data, thresh):
        img = cv2.imdecode(numpy.fromstring(image_data, numpy.uint8), cv2.IMREAD_UNCHANGED)
        return self.detector.detect(img, thresh)
    
    def stop(self):
        self.running = False
        self.trainer.stop()
    
    def run(self):
        while self.running:
            pass
