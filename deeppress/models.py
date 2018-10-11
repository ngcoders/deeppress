from keras import backend as K
from keras.models import Model
from keras.layers import Input, Flatten, Dense
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
import requests
import os
from deeppress.config import config
from sklearn.metrics import confusion_matrix
from glob import glob
import logging
import keras
import tensorflow as tf
configuration = tf.ConfigProto( device_count = {'GPU': 1} ) 
sess = tf.Session(config=configuration) 
keras.backend.set_session(sess)
url = os.path.join(config.WP_MODULES_URL, "/dp_models")
_logger = logging.getLogger('backend.models')


def get_data(endpoint):
    response = requests.request("GET", endpoint, auth=(config.WP_USERNAME, config.PASSWORD), timeout=10)
    result = response.json()
    if 'id' not in result['data'].keys():
        _logger.error("Invalid data")
        result = False
    return result


def get_model(model_id):
    """This function returns the file name (for building directory) and the model
    architecture (for compiling model) required for the job
    """
    
    _logger.debug("getting model filename and architecture")
    result = get_data(url)
    for res in result['data']:
        id_ = int(res['id'])
        if id_ == model_id:
            filename = res['file_name']
            architecture = res['architecture']
    
    if filename and architecture:
        return filename, architecture
    else:
        _logger.error("Invalid Model")
        return False, False


def compile_model(architecture, categories_id):
    """This function takes in architecture and list of categories as arguments to
    compile a model (Pre-trained on imagenet dataset) with suitable output layer 
    using the concept of transfer learning
    """

    _logger.debug("compiling model")
    nb_classes = len(categories_id)
    K.clear_session()
    input_tensor = Input(shape = (100,100,3))
    if (architecture == 'InceptionV3'):
        model, gen = inception(nb_classes, input_tensor)
        return model, gen
    elif (architecture == 'ResNet50'):
        model, gen = resnet(nb_classes, input_tensor)
        return model, gen
    elif (architecture == 'VGG16'):
        model, gen = vgg16(nb_classes, input_tensor)
        return model, gen
    elif (architecture == 'VGG19'):
        model, gen = vgg19(nb_classes, input_tensor)
        return model, gen
    elif (architecture == 'Xception'):
        model, gen = xception(nb_classes, input_tensor)
        return model, gen
    elif (architecture == 'InceptionResNetV2'):
        model, gen = inception_resnet(nb_classes, input_tensor)
        return model, gen
    elif (architecture == 'MobileNet'):
        model, gen = mobilenet(nb_classes, input_tensor)
        return model, gen
    elif (architecture == 'DenseNet'):
        model, gen = densenet(nb_classes, input_tensor)
        return model, gen
    elif (architecture == 'NASNet'):
        model, gen = nasnet(nb_classes, input_tensor)
        return model, gen
    elif (architecture == 'MobileNetV2'):
        model, gen = mobilenet_v2(nb_classes, input_tensor)
        return model, gen
    else:
        _logger.error("Invalid Model Selected")
        return False, False

def add_output_layers(model, nb_classes):
    for layer in model.layers:
        layer.trainable = False
    x = Flatten()(model.output)
    prediction = Dense(nb_classes, activation = 'softmax')(x)
    model_final = Model(inputs = model.input, outputs = prediction)
    try:
        model_final.compile(loss = 'categorical_crossentropy', optimizer = 'rmsprop', metrics = ['accuracy'])
        return model_final
    except Exception as e:
        _logger.error(e)
        return False


def gen_creator(preprocess_input):
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
    return gen


def inception(nb_classes, input_tensor):
    from keras.applications.inception_v3 import InceptionV3, preprocess_input
    model = InceptionV3(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    model_final = add_output_layers(model, nb_classes)
    gen = gen_creator(preprocess_input)
    return model_final, gen


def resnet(nb_classes, input_tensor):
    from keras.applications.resnet50 import ResNet50, preprocess_input
    model = ResNet50(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    model_final = add_output_layers(model, nb_classes)
    gen = gen_creator(preprocess_input)
    return model_final, gen


def vgg16(nb_classes, input_tensor):
    from keras.applications.vgg16 import VGG16, preprocess_input    
    model = VGG16(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    model_final = add_output_layers(model, nb_classes)
    gen = gen_creator(preprocess_input)
    return model_final, gen


def vgg19(nb_classes, input_tensor):
    from keras.applications.vgg19 import VGG19, preprocess_input    
    model = VGG19(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    model_final = add_output_layers(model, nb_classes)
    gen = gen_creator(preprocess_input)
    return model_final, gen


def xception(nb_classes, input_tensor):
    from keras.applications.xception import Xception, preprocess_input    
    model = Xception(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    model_final = add_output_layers(model, nb_classes)
    gen = gen_creator(preprocess_input)
    return model_final, gen


def inception_resnet(nb_classes, input_tensor):
    from keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input    
    model = InceptionResNetV2(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    model_final = add_output_layers(model, nb_classes)
    gen = gen_creator(preprocess_input)
    return model_final, gen


def mobilenet(nb_classes, input_tensor):
    from keras.applications.mobilenet import MobileNet, preprocess_input    
    model = MobileNet(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    model_final = add_output_layers(model, nb_classes)
    gen = gen_creator(preprocess_input)
    return model_final, gen


def densenet(nb_classes, input_tensor):
    from keras.applications.densenet import DenseNet121, preprocess_input    
    model = DenseNet121(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    model_final = add_output_layers(model, nb_classes)
    gen = gen_creator(preprocess_input)
    return model_final, gen


def nasnet(nb_classes, input_tensor):
    from keras.applications.nasnet import NASNetMobile, preprocess_input    
    model = NASNetMobile(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    model_final = add_output_layers(model, nb_classes)
    gen = gen_creator(preprocess_input)
    return model_final, gen


def mobilenet_v2(nb_classes, input_tensor):
    from keras.applications.mobilenetv2 import MobileNetV2, preprocess_input    
    model = MobileNetV2(input_tensor = input_tensor, weights = 'imagenet', include_top = False)
    model_final = add_output_layers(model, nb_classes)
    gen = gen_creator(preprocess_input)
    return model_final, gen


#filename, architecture = get_model(1)
#print(filename, architecture)
#model, gen = compile_model('InceptionV3',[1,2])
#print(model.summary())

