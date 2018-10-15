import json
import requests
import numpy as np
from PIL import Image, ImageFile
from io import BytesIO
from deeppress.config import config
import os
import logging

_logger = logging.getLogger('backend.predict')


ImageFile.LOAD_TRUNCATED_IMAGES = True

def model_load(filename):
    """This function loads the .h5 model file for the filename argument"""
    from keras.models import load_model
    path = os.path.join(config.TRAINED_MODELS_DATA, filename)
    model = load_model(os.path.join(path,('{}.h5'.format(filename))))
    if not model == None:
        flag = 1
    else:
        flag = 0
        _logger.error("Model not found")
    return flag, model

def get_image(im_url):
    """This function fetches the image for the given path so that it can be 
    classified
    """
    
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
    
    path = os.path.join(config.TRAINED_MODELS_DATA, filename) + '/labels.txt'
    flag =1
    try:
        with open(path) as json_file:
            data = json.load(json_file)
    except Exception as e:
        flag = 0
        _logger.error(e)
    labels = {}
    for p in data['category']:
        labels[p['index']] = p['name']
    return flag, labels


def predict_class(img, model, labels):
    """This function finally predicts the category for the given image and 
    classifies it while retturning the class ID, class name and the confidence
    score
    """
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
        final_predictions[predicted_class[i]] = round(confidence[i].astype(float), 2)
    return final_predictions
