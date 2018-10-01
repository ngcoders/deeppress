from keras import backend as K
from keras.models import Model
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
import tensorflow as tf
config = tf.ConfigProto( device_count = {'GPU': 1} ) 
sess = tf.Session(config=config) 
keras.backend.set_session(sess)
from keras.callbacks import EarlyStopping
import logging

_logger = logging.getLogger('backend.train')

batch_size = 16 #constrained to GPU capacity
epochs = 100
input_size=[100,100]
def create_gens(train_path, gen):
    _logger.debug("Creating Data Generators")
    image_files = glob(train_path + '/*/*.jp*g')
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
    return train_generator, test_generator, image_files, class_indices


def start_training(model, train_generator, test_generator, image_files, filename):
    _logger.debug("Start Training")
    callbacks = [EarlyStopping(monitor='val_loss', min_delta=0, patience=5, verbose=0, mode='auto', baseline=None)]
    r = model.fit_generator(
      train_generator,
      validation_data=test_generator,
      epochs=epochs,
      callbacks = callbacks,
      steps_per_epoch= (0.8 * len(image_files)) // batch_size,
      validation_steps=(0.2 * len(image_files)) // batch_size,
    )  
    path = '{}/model/'.format(filename)
    os.makedirs(path)
    model_file = os.path.abspath(path + ('{}.h5'.format(filename)))
    model.save(model_file)
    #print("Trained model saved at {}".format(model_file))
    return model_file, r.history['acc'][-1], r.history['loss'][-1], r.history['val_acc'][-1], r.history['val_loss'][-1]

def create_labels(cat_dict, filename, class_indices):
    _logger.debug("Mapping labels")
    label={}
    label['category']=[]
    for key in cat_dict:
        label['category'].append({
             'id' : key,
             'name' : cat_dict[key],
             'index' : class_indices[str(key)]
        })
    label_path = '{}/model/'.format(filename)
    with open((label_path + 'labels.txt'), 'w') as outfile:  
         json.dump(label, outfile)
    return label_path

#cat_dict = {2 : "asdasd", 3 : "qweqwe"}
#filename = "wtpsth"
#class_indices = {'2' : 0, '3' : 1}
#create_labels(cat_dict, filename, class_indices)


