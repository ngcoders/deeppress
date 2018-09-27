from keras import backend as K
from keras.models import Model
from keras.layers import Input, Flatten, Dense
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator


from sklearn.metrics import confusion_matrix
from glob import glob

import keras
import tensorflow as tf
config = tf.ConfigProto( device_count = {'GPU': 1} ) 
sess = tf.Session(config=config) 
keras.backend.set_session(sess)

url = "http://192.168.0.12:8000/wp-json/deeppress/v1/dp_models"

headers = {
    'Authorization': "Basic YWRtaW46YWRtaW4=",
    'Cache-Control': "no-cache",
    'Postman-Token': "36b03303-664a-4c86-aeda-0561d9799ac5"
    }


def get_data(endpoint):
    response = requests.request("GET", endpoint, headers=headers)
    result = response.json()
    return result


def get_model(model_id):
    result = get_data(url)
    for res in result['data']:
        id_ = int(res['id'])
        if id_ == model_id:
           name = res['name']
           architecture = res['architecture']
    return name, architecture

def compile_model(architecture, categories_id):
    nb_classes = len(categories_id)
    if architecture == 'InceptionV3':
       model, gen, input_size = inception(nb_classes)
       return model, gen, input_size
    if architecture == 'ResNet50':
       model, gen, input_size = resnet(nb_classes)
       return model, gen, input_size
    if architecture == 'VGG16':
       model, gen, input_size = vgg16(nb_classes)
       return model, gen, input_size
    if architecture == 'VGG19':
       model, gen, input_size = vgg19(nb_classes)
       return model, gen, input_size
    if architecture == 'Xception':
       model, gen, input_size = xception(nb_classes)
       return model, gen, input_size
    if architecture == 'InceptionResNetV2':
       model, gen, input_size = inception_resnet(nb_classes)
       return model, gen, input_size
    if architecture == 'MobileNet':
       model, gen, input_size = mobilenet(nb_classes)
       return model, gen, input_size
    if architecture == 'DenseNet':
       model, gen, input_size = densenet(nb_classes)
       return model, gen, input_size
    if architecture == 'NASNet':
       model, gen, input_size = nasnet(nb_classes)
       return model, gen, input_size
    if architecture == 'MobileNetV2':
       model, gen, input_size = mobilenet_v2(nb_classes)
       return model, gen, input_size
    else:
       raise Exception('Invalid Model Selection')


def inception(nb_classes):
    from keras.applications.inception_v3 import InceptionV3, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (299,299,3))
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
    INPUT_SIZE = [299,299]
    return model_final, gen, INPUT_SIZE

def resnet(nb_classes):
    from keras.applications.resnet50 import ResNet50, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (224,224,3))
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
    INPUT_SIZE = [224,224]
    return model_final, gen, INPUT_SIZE

def vgg16(nb_classes):
    from keras.applications.vgg16 import VGG16, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (224,224,3))
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
    INPUT_SIZE = [224,224]
    return model_final, gen, INPUT_SIZE

def vgg19(nb_classes):
    from keras.applications.vgg19 import VGG19, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (224,224,3))
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
    INPUT_SIZE = [224,224]
    return model_final, gen, INPUT_SIZE

def xception(nb_classes):
    from keras.applications.xception import Xception, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (299,299,3))
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
    INPUT_SIZE = [299,299]
    return model_final, gen, INPUT_SIZE

def inception_resnet(nb_classes):
    from keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (299,299,3))
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
    INPUT_SIZE = [299,299]
    return model_final, gen, INPUT_SIZE

def mobilenet(nb_classes):
    from keras.applications.mobilenet import MobileNet, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (224,224,3))
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
    INPUT_SIZE = [224,224]
    return model_final, gen, INPUT_SIZE

def densenet(nb_classes):
    from keras.applications.densenet import DenseNet121, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (224,224,3))
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
    INPUT_SIZE = [224,224]
    return model_final, gen

def nasnet(nb_classes):
    from keras.applications.nasnet import NASNetMobile, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (224,224,3))
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
    INPUT_SIZE = [224,224]
    return model_final, gen, INPUT_SIZE 

def mobilenet_v2(nb_classes):
    from keras.applications.mobilenetv2 import MobileNetV2, preprocess_input
    K.clear_session()
    input_tensor = Input(shape = (224,224,3))
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
    INPUT_SIZE = [224,224]
    return model_final, gen, INPUT_SIZE


model, gen, INPUT_SIZE = compile_model('InceptionV3',[1,2])
print(model.summary(), INPUT_SIZE)

