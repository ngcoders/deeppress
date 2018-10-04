from keras import backend as K
from keras.models import Model
from keras.layers import Input, Flatten, Dense
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
import requests

from sklearn.metrics import confusion_matrix
from glob import glob
import logging
import keras
import tensorflow as tf
configuration = tf.ConfigProto( device_count = {'GPU': 1} ) 
sess = tf.Session(config=configuration) 
keras.backend.set_session(sess)

url = "http://192.168.0.12:8000/wp-json/deeppress/v1/dp_models"

headers = {
    'Authorization': "Basic YWRtaW46YWRtaW4=",
    'Cache-Control': "no-cache",
    'Postman-Token': "36b03303-664a-4c86-aeda-0561d9799ac5"
    }
_logger = logging.getLogger('backend.models')

def get_data(endpoint):
    response = requests.request("GET", endpoint, headers=headers)
    result = response.json()
    return result


def get_model(model_id):
    """This function returns the file name (for building directory) and the model architecture (for compiling model) required for the job"""
    
    _logger.debug("getting model filename and architecture")
    result = get_data(url)
    for res in result['data']:
        id_ = int(res['id'])
        if id_ == model_id:
           filename = res['file_name']
           architecture = res['architecture']
    return filename, architecture

def compile_model(architecture, categories_id):
    """This function takes in architecture and list of categories as arguments to compile a model (Pre-trained on imagenet dataset)
       with suitable output layer using the concept of transfer learning"""

    _logger.debug("compiling model")
    nb_classes = len(categories_id)
    if architecture == 'InceptionV3':
       model, gen = inception(nb_classes)
       return model, gen
    if architecture == 'ResNet50':
       model, gen = resnet(nb_classes)
       return model, gen
    if architecture == 'VGG16':
       model, gen = vgg16(nb_classes)
       return model, gen
    if architecture == 'VGG19':
       model, gen = vgg19(nb_classes)
       return model, gen
    if architecture == 'Xception':
       model, gen = xception(nb_classes)
       return model, gen
    if architecture == 'InceptionResNetV2':
       model, gen = inception_resnet(nb_classes)
       return model, gen
    if architecture == 'MobileNet':
       model, gen = mobilenet(nb_classes)
       return model, gen
    if architecture == 'DenseNet':
       model, gen = densenet(nb_classes)
       return model, gen
    if architecture == 'NASNet':
       model, gen = nasnet(nb_classes)
       return model, gen
    if architecture == 'MobileNetV2':
       model, gen = mobilenet_v2(nb_classes)
       return model, gen
    else:
       raise Exception('Invalid Model Selection')


def inception(nb_classes):
    from keras.applications.inception_v3 import InceptionV3, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (100,100,3))
    model = InceptionV3(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    for layer in model.layers:
        layer.trainable = False
    x = Flatten()(model.output)
    prediction = Dense(nb_classes, activation = 'softmax')(x)
    model_final = Model(inputs = model.input, outputs = prediction)
    model_final.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])
    gen = ImageDataGenerator(
       featurewise_center=True, samplewise_center=True,
       rotation_range=20,
       width_shift_range=0.1,
       height_shift_range=0.1,
       shear_range=0.1,
       zoom_range=0.1,
       horizontal_flip=True,
       vertical_flip=True,
       featurewise_std_normalization=True, samplewise_std_normalization=True,
       preprocessing_function=preprocess_input,
       validation_split = 0.8
    )
    return model_final, gen

def resnet(nb_classes):
    from keras.applications.resnet50 import ResNet50, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (100,100,3))
    model = ResNet50(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    for layer in model.layers:
        layer.trainable = False
    x = Flatten()(model.output)
    prediction = Dense(nb_classes, activation = 'softmax')(x)
    model_final = Model(inputs = model.input, outputs = prediction)
    model_final.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])
    gen = ImageDataGenerator(
       featurewise_center=True, samplewise_center=True,
       rotation_range=20,
       width_shift_range=0.1,
       height_shift_range=0.1,
       shear_range=0.1,
       zoom_range=0.1,
       horizontal_flip=True,
       vertical_flip=True,
       featurewise_std_normalization=True, samplewise_std_normalization=True,
       preprocessing_function=preprocess_input,
       validation_split = 0.8
    )
    return model_final, gen

def vgg16(nb_classes):
    from keras.applications.vgg16 import VGG16, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (100,100,3))
    model = VGG16(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    for layer in model.layers:
        layer.trainable = False
    x = Flatten()(model.output)
    prediction = Dense(nb_classes, activation = 'softmax')(x)
    model_final = Model(inputs = model.input, outputs = prediction)
    model_final.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])
    gen = ImageDataGenerator(
       featurewise_center=True, samplewise_center=True,
       rotation_range=20,
       width_shift_range=0.1,
       height_shift_range=0.1,
       shear_range=0.1,
       zoom_range=0.1,
       horizontal_flip=True,
       vertical_flip=True,
       featurewise_std_normalization=True, samplewise_std_normalization=True,
       preprocessing_function=preprocess_input,
       validation_split = 0.8
    )
    return model_final, gen

def vgg19(nb_classes):
    from keras.applications.vgg19 import VGG19, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (100,100,3))
    model = VGG19(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    for layer in model.layers:
        layer.trainable = False
    x = Flatten()(model.output)
    prediction = Dense(nb_classes, activation = 'softmax')(x)
    model_final = Model(inputs = model.input, outputs = prediction)
    model_final.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])
    gen = ImageDataGenerator(
       featurewise_center=True, samplewise_center=True,
       rotation_range=20,
       width_shift_range=0.1,
       height_shift_range=0.1,
       shear_range=0.1,
       zoom_range=0.1,
       horizontal_flip=True,
       vertical_flip=True,
       featurewise_std_normalization=True, samplewise_std_normalization=True,
       preprocessing_function=preprocess_input,
       validation_split = 0.8
    )
    return model_final, gen

def xception(nb_classes):
    from keras.applications.xception import Xception, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (100,100,3))
    model = Xception(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    for layer in model.layers:
        layer.trainable = False
    x = Flatten()(model.output)
    prediction = Dense(nb_classes, activation = 'softmax')(x)
    model_final = Model(inputs = model.input, outputs = prediction)
    model_final.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])
    gen = ImageDataGenerator(
       featurewise_center=True, samplewise_center=True,
       rotation_range=20,
       width_shift_range=0.1,
       height_shift_range=0.1,
       shear_range=0.1,
       zoom_range=0.1,
       horizontal_flip=True,
       vertical_flip=True,
       featurewise_std_normalization=True, samplewise_std_normalization=True,
       preprocessing_function=preprocess_input,
       validation_split = 0.8
    )
    return model_final, gen

def inception_resnet(nb_classes):
    from keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (100,100,3))
    model = InceptionResNetV2(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    for layer in model.layers:
        layer.trainable = False
    x = Flatten()(model.output)
    prediction = Dense(nb_classes, activation = 'softmax')(x)
    model_final = Model(inputs = model.input, outputs = prediction)
    model_final.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])
    gen = ImageDataGenerator(
       featurewise_center=True, samplewise_center=True,
       rotation_range=20,
       width_shift_range=0.1,
       height_shift_range=0.1,
       shear_range=0.1,
       zoom_range=0.1,
       horizontal_flip=True,
       vertical_flip=True,
       featurewise_std_normalization=True, samplewise_std_normalization=True,
       preprocessing_function=preprocess_input,
       validation_split = 0.8
    )
    return model_final, gen

def mobilenet(nb_classes):
    from keras.applications.mobilenet import MobileNet, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (100,100,3))
    model = MobileNet(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    for layer in model.layers:
        layer.trainable = False
    x = Flatten()(model.output)
    prediction = Dense(nb_classes, activation = 'softmax')(x)
    model_final = Model(inputs = model.input, outputs = prediction)
    model_final.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])
    gen = ImageDataGenerator(
       featurewise_center=True, samplewise_center=True,
       rotation_range=20,
       width_shift_range=0.1,
       height_shift_range=0.1,
       shear_range=0.1,
       zoom_range=0.1,
       horizontal_flip=True,
       vertical_flip=True,
       featurewise_std_normalization=True, samplewise_std_normalization=True,
       preprocessing_function=preprocess_input,
       validation_split = 0.8
    )
    return model_final, gen

def densenet(nb_classes):
    from keras.applications.densenet import DenseNet121, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (100,100,3))
    model = DenseNet121(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    for layer in model.layers:
        layer.trainable = False
    x = Flatten()(model.output)
    prediction = Dense(nb_classes, activation = 'softmax')(x)
    model_final = Model(inputs = model.input, outputs = prediction)
    model_final.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])
    gen = ImageDataGenerator(
       featurewise_center=True, samplewise_center=True,
       rotation_range=20,
       width_shift_range=0.1,
       height_shift_range=0.1,
       shear_range=0.1,
       zoom_range=0.1,
       horizontal_flip=True,
       vertical_flip=True,
       featurewise_std_normalization=True, samplewise_std_normalization=True,
       preprocessing_function=preprocess_input,
       validation_split = 0.8
    )
    return model_final, gen

def nasnet(nb_classes):
    from keras.applications.nasnet import NASNetMobile, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (100,100,3))
    model = NASNetMobile(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    for layer in model.layers:
        layer.trainable = False
    x = Flatten()(model.output)
    prediction = Dense(nb_classes, activation = 'softmax')(x)
    model_final = Model(inputs = model.input, outputs = prediction)
    model_final.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])
    gen = ImageDataGenerator(
       featurewise_center=True, samplewise_center=True,
       rotation_range=20,
       width_shift_range=0.1,
       height_shift_range=0.1,
       shear_range=0.1,
       zoom_range=0.1,
       horizontal_flip=True,
       vertical_flip=True,
       featurewise_std_normalization=True, samplewise_std_normalization=True,
       preprocessing_function=preprocess_input,
       validation_split = 0.8
    )
    return model_final, gen

def mobilenet_v2(nb_classes):
    from keras.applications.mobilenetv2 import MobileNetV2, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (100,100,3))
    model = MobileNetV2(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    for layer in model.layers:
        layer.trainable = False
    x = Flatten()(model.output)
    prediction = Dense(nb_classes, activation = 'softmax')(x)
    model_final = Model(inputs = model.input, outputs = prediction)
    model_final.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])
    gen = ImageDataGenerator(
       featurewise_center=True, samplewise_center=True,
       rotation_range=20,
       width_shift_range=0.1,
       height_shift_range=0.1,
       shear_range=0.1,
       zoom_range=0.1,
       horizontal_flip=True,
       vertical_flip=True,
       featurewise_std_normalization=True, samplewise_std_normalization=True,
       preprocessing_function=preprocess_input,
       validation_split = 0.8
    )
    return model_final, gen

#filename, architecture = get_model(1)
#print(filename, architecture)
#model, gen = compile_model('InceptionV3',[1,2])
#print(model.summary())

