import json
from keras.models import load_model
import numpy as np
import cv2
import urllib.request
base_url = "http://192.168.0.12:8000"
def model_load(filename):
    model = load_model('{}/model/{}.h5'.format(filename, filename))
    return model

def get_image(im_url):
    url = base_url + im_url
    url_response = urllib.request.urlopen(url)
    img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, -1)
    img = cv2.resize(img, (100,100))
    img = np.reshape(img, (1,100,100,3))
    return img

def get_labels(filename):
    path = '/home/aditya/{}/model/labels.txt'.format(filename)
    with open(path) as json_file:  
         data = json.load(json_file)
    labels = {}
    names = {}
    for p in data['category']:
        labels[p['index']] = p['id']
        names[p['id']]=p['name']
    return labels, names

def predict_class(img, model, labels, names):
    p = model.predict(img)
    pred = np.argmax(p, axis=1)
    predicted_id = labels[pred]
    predicted_class = names[predicted_id] 
    confidence = p[0][pred]
    return predicted_id, predicted_class, confidence
#labels, names = get_labels("wtpsth")
#print(labels, names)
