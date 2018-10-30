from multiprocessing import Process
import logging
import os
import shutil

import cv2
import numpy as np

from deeppress.models import get_model, compile_model
from deeppress.dataset import request_categories, prepare_dataset
from deeppress.train import create_gens, start_training, create_labels
from deeppress.predict import model_load, get_image, get_labels, predict_class
from deeppress import api

_logger = logging.getLogger('deeppress.main')


class ClassificationJob(Process):
    """start a new classification job"""
    
    def __init__(self, job):
        """Start a new training Job"""
        super(ClassificationJob, self).__init__()
        self.job = job
        self.model = None
        self.groups = []
        self.data_dir = None
        self.status = {
            "status": "created",
            "ETA": None,
            "job": job
        }

        

    def run(self):
        model_id = self.job['model']
        categories = self.job['categories']
        epochs = int(self.job['steps'])
        filename, architecture = get_model(model_id)
        cat_dict, categories_id, categories_name = request_categories(categories)
        if categories_id:
            path = prepare_dataset(categories_id, filename, self.job, cat_dict)
            model, gen = compile_model(architecture, categories_name)
            if (not path == None) and (not model == None):
                train_generator, test_generator, image_files, class_indices = create_gens(path, gen)
                if (not train_generator == None) and (not test_generator == None):
                    training_complete, train_accuracy, train_loss, val_accuracy, val_loss = start_training(model, train_generator, test_generator, image_files, filename, self.job, epochs)
                    create_labels(filename, class_indices)
                    if training_complete:
                        api.update_job(self.job['id'],
                        {'done' : 1,
                        'status': 'complete', 
                        'remarks' : 'train_accuracy : {}, train_loss : {}, val_accuracy : {}, val_loss : {}'.format(train_accuracy, train_loss, val_accuracy, val_loss)})
                    else:
                        api.update_job(self.job['id'], 
                        {'done' : 0,
                        'status': 'incomplete', 
                        'remarks' : 'train_accuracy : {}, train_loss : {}, val_accuracy : {}, val_loss : {}'.format(train_accuracy, train_loss, val_accuracy, val_loss)})
                else:
                    print("Error : Could not train model")
                    api.update_job(self.job['id'], {'done' : 0, 'status': 'invalid', 'remarks': "Could not train due to invalid generators"})
            else:
                api.update_job(self.job['id'], {'done' : 0, 'status': 'invalid', 'remarks': "Could not train due to invalid model compilation"})
            _logger.debug("Clean up dataset")
            shutil.rmtree(path)
        else:
            api.update_job(self.job['id'], {'done' : 0, 'status': 'invalid', 'remarks': "Could not train as dataset or categories are not enough"})
 

def predictor(img, filename):
    model = model_load(filename)
    img = cv2.imdecode(np.fromstring(img, np.uint8), cv2.IMREAD_UNCHANGED)
    if not isinstance(img, np.ndarray):
        return False
    else:
        if len(img.shape) > 2 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        img = cv2.resize(img,(100,100))
        img = np.reshape(img, (1,100,100,3)) 
        if (not model == None):
            labels = get_labels(filename)
            if not labels == None:
                prediction = predict_class(img, model, labels)
            else:
                return False
        else:
            return False
        return prediction


