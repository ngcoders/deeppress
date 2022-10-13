import json

import requests
import os
import logging

import numpy as np
from PIL import Image, ImageFile
from io import BytesIO

from deeppress.config import config

_logger = logging.getLogger('deeppress.predict')

ImageFile.LOAD_TRUNCATED_IMAGES = True

def model_load(filename):
    """This function loads the .h5 model file for the filename argument"""

    from keras.models import load_model
    _logger.debug("getting model")
    path = os.path.join(config.TRAINED_MODELS_DATA, filename)
    model = load_model(os.path.join(path,('{}.h5'.format(filename))))
    return model

def get_image(im_url):
    """This function fetches the image for the given path so that it can be 
    classified
    """
    _logger.debug("getting image")
    try:
        img = Image.open(BytesIO(im_url))
        img = img.resize((100,100))
        img = np.reshape(img, (1,100,100,3))
    except Exception as e:
        _logger.error(e)
        flag = 0
        img = False
    return flag, img


def get_labels(filename):
    """This function parses the label file (.txt) as a json file to load the 
    categories for which the model has been trained
    """
    _logger.debug("getting labels")
    path = os.path.join(config.TRAINED_MODELS_DATA, filename) + '/labels.txt'
    try:
        with open(path) as json_file:
            data = json.load(json_file)
    except Exception as e:
        _logger.error(e)
        return None
    labels = {}
    for p in data['category']:
        labels[p['index']] = p['name']
    return labels


def predict_class(img, model, labels):
    """This function finally predicts the category for the given image and 
    classifies it while retturning the class ID, class name and the confidence
    score
    """
    _logger.debug("predicting")
    try:
        p = model.predict(img)
    except Exception as e:
        _logger.error(e)
        return False, False
    pred = np.argmax(p, axis=1)
    predicted_class = labels
    confidence = p[0]
    final_predictions = {}
    for i in range(0,len(confidence)):
        final_predictions[predicted_class[i]] = float(format(confidence[i], '0.2f'))
    return final_predictions

