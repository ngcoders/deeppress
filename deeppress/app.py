import time
from multiprocessing import Queue
from deeppress.tf2_detection import TF2DetectorModel as DetectorModel
from deeppress.trainer import TrainingApp
from deeppress.config import config

class DeepPressApp():
    def __init__(self):
        # super(Process, self).__init__()
        self.running = True
        self.training_job = None
        self.mode_file = None
        self.trainer = TrainingApp()

        # for detector
        self.request = Queue()
        self.response = Queue()
        self.detector = DetectorModel(True, config.EXPORTED_MODELS, self.request, self.response)
        self.detector.start()
        self.is_detector_using_gpu = True

    def is_training(self):
        return self.trainer.current_job and self.trainer.current_job.is_alive()

    def start_training(self):
        if self.trainer:
            self.stop_detector()
            self.trainer.start()

    def stop_training(self):
        if self.trainer:
            self.trainer.stop()

    def get_training_status(self):
        return self.trainer.status()

    def current_model(self):
        return self.mode_file
    
    def detect_box(self, data):
        if not self.is_detector_using_gpu and not self.is_training():
            # when the training is over, use gpu for detection
            self.stop_detector()
        if not self.detector:
            # if detector is not initialized, initialize detector
            self.detector = DetectorModel(not self.is_training(), config.EXPORTED_MODELS, self.request, self.response)
            self.detector.start()
            self.is_detector_using_gpu = not self.is_training()
        # send data to the process
        self.request.put(data)
        time_start = time.time()
        while True:
            if time.time() - time_start > 100:
                # wait timeout
                return {'success': False, 'error': 'Timeout'}
            if self.request.empty():
                continue
            response = self.response.get()
            print(response, flush=True)
            return response

    def stop_detector(self):
        if self.detector:
            self.detector.stop()
            self.detector.terminate()
            self.detector = None

    # def load_model(self, model):
    #     self.detector.load(config.EXPORTED_MODELS, model)

    # def unload_model(self):
    #     self.detector.unload()

    # def detect(self, image_data, thresh):
    #     img = cv2.imdecode(numpy.fromstring(image_data, numpy.uint8), cv2.IMREAD_UNCHANGED)
    #     return self.detector.detect(img, thresh)
    
    def stop(self):
        self.running = False
        self.trainer.stop()
        self.stop_detector()
    
    def run(self):
        while self.running:
            pass
