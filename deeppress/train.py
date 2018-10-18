import json
from glob import glob
import os
import logging

import numpy as np

from deeppress import api
from deeppress.config import config


_logger = logging.getLogger('deeppress.train')

batch_size = 8 #constrained to GPU capacity
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
        train_generator = None
        test_generator = None
        image_files = None
        class_indices= None
    return train_generator, test_generator, image_files, class_indices


def start_training(model, train_generator, test_generator, image_files, filename, job, epochs):
    """This function finally trains the classifier to classify the images according
    to the category labels found in the dataset. After training is complete the 
    trained model (.h5 file) is saved in the '/<filename>/model/' local directory
    and returns the performance measures such as training accuracy, training loss,
    validation accuracy and validation loss
    """
    
    from keras.models import load_model
    from keras.callbacks import ModelCheckpoint

    _logger.debug("Start Training")
    if epochs == 0:
        _logger.error("cannot train for 0 epochs")
        return False, False, False, False, False
    training_complete = 0
    path = os.path.join(config.TRAINED_MODELS_DATA, filename)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        callbacks = [ModelCheckpoint(
            filepath = os.path.join(path, '{}tmp.h5'.format(filename)), 
            monitor='val_loss', 
            verbose=0, 
            save_best_only=False, 
            save_weights_only=False, 
            mode='auto', 
            period=int(0.1 * epochs))]
        state = api.update_job_state(job, 'training', 'Start training for {} epochs'.format(epochs))
        history_acc = []
        for i in range(1, epochs+1):
            r = model.fit_generator(
                train_generator,
                validation_data=test_generator,
                epochs=1,
                callbacks = callbacks,
                steps_per_epoch= (0.8 * len(image_files)) / batch_size,
                validation_steps=(0.2 * len(image_files)) / batch_size,
            )
            history_acc.append(r.history['acc'][-1])
            with open(os.path.join(os.path.join(config.TRAINED_MODELS_DATA, filename), 'info.txt'), 'w') as outfile:
                outfile.write(str(i))
        
        if len(history_acc) < epochs:
            training_complete = 0
            return training_complete, r.history['acc'][-1], r.history['loss'][-1], r.history['val_acc'][-1], r.history['val_loss'][-1]
        else:
            model_file = os.path.join(path, ('{}.h5'.format(filename)))
            model.save(model_file)
            training_complete = 1
            return training_complete, r.history['acc'][-1], r.history['loss'][-1], r.history['val_acc'][-1], r.history['val_loss'][-1]
    else:
        _logger.debug("Loading existing model file")
        model_ = load_model(os.path.join(path, '{}tmp.h5'.format(filename)))
        with open(os.path.join(os.path.join(config.TRAINED_MODELS_DATA, filename), 'info.txt'), 'r') as outfile:
                last_epoch = int(outfile.read())
        if not model_ == None:
            callbacks = [ModelCheckpoint(
                filepath = os.path.join(path, '{}tmp.h5'.format(filename)), 
                monitor='val_loss', 
                verbose=0, 
                save_best_only=False, 
                save_weights_only=False, 
                mode='auto', 
                period=int(0.1 * epochs))]
            state = api.update_job_state(job, 'training', 'Start training for {} epochs'.format(epochs))
            history_acc = []
            if last_epoch == epochs:
                for i in range(1, epochs+1):
                    r = model_.fit_generator(
                        train_generator,
                        validation_data=test_generator,
                        epochs=1,
                        callbacks = callbacks,
                        steps_per_epoch= (0.8 * len(image_files)) / batch_size,
                        validation_steps=(0.2 * len(image_files)) / batch_size,
                    )
                    history_acc.append(r.history['acc'][-1])
                    with open(os.path.join(os.path.join(config.TRAINED_MODELS_DATA, filename), 'info.txt'), 'w') as outfile:
                        outfile.write(str(i))
            else:
                for i in range(1, (epochs+1)-last_epoch):
                    r = model_.fit_generator(
                        train_generator,
                        validation_data=test_generator,
                        epochs=1,
                        callbacks = callbacks,
                        steps_per_epoch= (0.8 * len(image_files)) / batch_size,
                        validation_steps=(0.2 * len(image_files)) / batch_size,
                    )
                    history_acc.append(r.history['acc'][-1])
                    with open(os.path.join(os.path.join(config.TRAINED_MODELS_DATA, filename), 'info.txt'), 'w') as outfile:
                        outfile.write(str(i+last_epoch))
        else:
            _logger.error("model file missing")
            return False, False, False, False, False
        if len(history_acc) < (epochs - last_epoch):
            training_complete = 0
            return training_complete, r.history['acc'][-1], r.history['loss'][-1], r.history['val_acc'][-1], r.history['val_loss'][-1]
        else:
            model_file = os.path.join(path,('{}.h5'.format(filename)))
            model_.save(model_file)
            training_complete = 1
            return training_complete, r.history['acc'][-1], r.history['loss'][-1], r.history['val_acc'][-1], r.history['val_loss'][-1]



def create_labels(filename, class_indices):
    """This function creates a text file for the label mapping according to their
    class indices as determined by the Image Data Generators. This label can be
    parsed for predictions over new images by parsing it by opening it as a json
    file
    """
    
    _logger.debug("Mapping labels")
    label={}
    label['category']=[]
    for key in class_indices:
        label['category'].append({
            'name' : key,
            'index' : class_indices[key]
        })
    label_path = os.path.join(config.TRAINED_MODELS_DATA, filename)
    with open(os.path.join(label_path, 'labels.txt'), 'w') as outfile:
        json.dump(label, outfile)
    return label_path