from multiprocessing import Process
from models import get_model, compile_model
from dataset import request_categories, prepare_dataset
from train import create_gens, start_training, create_labels
from predict import model_load, get_image, get_labels, predict_class
import api
import logging
_logger = logging.getLogger('backend.main')


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
        filename, architecture = get_model(model_id)
        cat_dict, categories_id = request_categories(categories)
        flag, path = prepare_dataset(categories_id, filename, self.job)
        model, gen = compile_model(architecture, categories_id)
        if flag and model:
            train_generator, test_generator, image_files, class_indices = create_gens(path, gen)
            if train_generator and test_generator:
                train_accuracy, train_loss, val_accuracy, val_loss = start_training(model, train_generator, test_generator, image_files, filename, self.job)
                create_labels(cat_dict, filename, class_indices)
                api.update_job(self.job['id'], 
                {'done' : 1, 
                'train_accuracy' : train_accuracy, 
                'train_loss' : train_loss, 
                'val_accuracy' : val_accuracy, 
                'val_loss' : val_loss})
            else:
                print("Error : Could not train model")
                api.update_job(self.job['id'], {'done' : 0, 'remarks': "Could not train due to error"})
        else:
            api.update_job(self.job['id'], {'done' : 0, 'remarks': "Could not train due to error"})
 

def predictor(img_url, filename):
    model = model_load(filename)
    img = get_image(img_url)
    labels, names = get_labels(filename)
    predicted_id, predicted_class, confidence = predict_class(img, model, labels, names)
    return predicted_id, predicted_class, confidence
