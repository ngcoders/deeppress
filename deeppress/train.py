from keras import backend as K
from keras.models import Model, load_model
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
import cv2
import json
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from glob import glob
import os
import keras
import api
import tensorflow as tf
from deeppress.config import config
configuration = tf.ConfigProto( device_count = {'GPU': 1} ) 
sess = tf.Session(config=configuration) 
keras.backend.set_session(sess)
from keras.callbacks import EarlyStopping, ModelCheckpoint
import logging

_logger = logging.getLogger('backend.train')

batch_size = 16 #constrained to GPU capacity
epochs = 20
input_size=[100,100]


def create_gens(train_path, gen):
    """This function creates and returns the Image Data Generators for training
    and validation subsets as specified by Keras to map the images with their
    category labels in order to be trained
    """

    _logger.debug("Creating Data Generators")
    image_files = glob(train_path + '/*/*.jp*g')
    try:
        train_generator = gen.flow_from_directory(
            train_path,
            target_size=input_size,
            shuffle=True,
            batch_size=batch_size,
            subset = "validation"
        )
        test_generator = gen.flow_from_directory(
            train_path,
            target_size=input_size,
            shuffle=True,
            batch_size=batch_size,
            subset = "training"
        )
        class_indices = train_generator.class_indices
    except FileNotFoundError:
        _logger.error("data generators invalid")
        train_generator = False
        test_generator = False
        image_files = False
        class_indices= False
    return train_generator, test_generator, image_files, class_indices


def start_training(model, train_generator, test_generator, image_files, filename, job, status):
    """This function finally trains the classifier to classify the images according
    to the category labels found in the dataset. After training is complete the 
    trained model (.h5 file) is saved in the '/<filename>/model/' local directory
    and returns the performance measures such as training accuracy, training loss,
    validation accuracy and validation loss
    """

    _logger.debug("Start Training")
    flag = 1
    path = os.path.join(config.TRAINED_MODELS_DATA, filename)
    if status == "Added":
        os.makedirs(path)
        callbacks = [ModelCheckpoint(
            filepath = os.path.join(path, '{}tmp.h5'.format(filename)), 
            monitor='val_loss', 
            verbose=0, 
            save_best_only=False, 
            save_weights_only=False, 
            mode='auto', 
            period=1)]
        state = api.update_job_state(job, 'training', 'Start training for {} epochs'.format(epochs))
        try:
            r = model.fit_generator(
                train_generator,
                validation_data=test_generator,
                epochs=epochs,
                callbacks = callbacks,
                steps_per_epoch= (0.8 * len(image_files)) // batch_size,
                validation_steps=(0.2 * len(image_files)) // batch_size,
            )
        except Exception:
            return False, False, False, False, False
        if len(r.history['acc']) < epochs:
            flag = 0
            return flag, r.history['acc'][-1], r.history['loss'][-1], r.history['val_acc'][-1], r.history['val_loss'][-1]
        else:
            model_file = os.path.join(path + ('{}.h5'.format(filename)))
            model.save(model_file)
            return flag, r.history['acc'][-1], r.history['loss'][-1], r.history['val_acc'][-1], r.history['val_loss'][-1]
    elif status == "incomplete":
        model = load_model(os.path.join(path, '{}tmp.h5'.format(filename)))
        callbacks = [ModelCheckpoint(
            filepath = os.path.join(path, '{}tmp.h5'.format(filename)), 
            monitor='val_loss', 
            verbose=0, 
            save_best_only=False, 
            save_weights_only=False, 
            mode='auto', 
            period=1)]
        state = api.update_job_state(job, 'training', 'Start training for {} epochs'.format(epochs))
        r = model.fit_generator(
            train_generator,
            validation_data=test_generator,
            epochs=epochs,
            callbacks = callbacks,
            steps_per_epoch= (0.8 * len(image_files)) // batch_size,
            validation_steps=(0.2 * len(image_files)) // batch_size,
        )
        if len(r.history['acc']) < epochs:
            flag = 0
            return flag, r.history['acc'][-1], r.history['loss'][-1], r.history['val_acc'][-1], r.history['val_loss'][-1]
        else:
            model_file = os.path.join(path + ('{}.h5'.format(filename)))
            model.save(model_file)
            return flag, r.history['acc'][-1], r.history['loss'][-1], r.history['val_acc'][-1], r.history['val_loss'][-1]



def create_labels(cat_dict, filename, class_indices):
    """This function creates a text file for the label mapping according to their
    class indices as determined by the Image Data Generators. This label can be
    parsed for predictions over new images by parsing it by opening it as a json
    file
    """
    
    _logger.debug("Mapping labels")
    label={}
    label['category']=[]
    for key in cat_dict:
        label['category'].append({
            'id' : key,
            'name' : cat_dict[key],
            'index' : class_indices[str(key)]
        })
    label_path = os.path.join(config.TRAINED_MODELS_DATA, filename)
    with open((label_path + 'labels.txt'), 'w') as outfile:
        json.dump(label, outfile)
    return label_path


#cat_dict = {2 : "asdasd", 3 : "qweqwe"}
#filename = "wtpsth"
#class_indices = {'2' : 0, '3' : 1}
#create_labels(cat_dict, filename, class_indices)


