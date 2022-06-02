import os
import sys
import logging
import argparse
import logging
from logging.handlers import RotatingFileHandler
from deeppress.config import config, load_config, DeepPressConfig


# -----------------------------------Logging----------------------------------
# if config.DEBUG:
#     LOG_LEVEL = logging.DEBUG
# else:
#     LOG_LEVEL = logging.INFO
LOG_LEVEL = logging.DEBUG
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(LOG_LEVEL)
log_file = '/tmp/deeppress.log'
print('log file: {}'.format(log_file))
fh = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=3)
fh.setLevel(LOG_LEVEL)
# create formatter and add it to the handlers
formatter = logging.Formatter(fmt='%(levelname).1s %(asctime)s.%(msecs).03d: %(message)s [%(pathname)s:%(lineno)d]', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
_LOGGER = logging.getLogger('deeppress')
_LOGGER.setLevel(LOG_LEVEL)
_LOGGER.addHandler(ch)
_LOGGER.addHandler(fh)
_LOGGER.propagate = False
_LOGGER.info('Booting Up')
# ----------------------------------------------------------------------------

from deeppress.app import DeepPressApp
from deeppress.bottle import install, route, run, request, hook, response
from deeppress.web import AuthPlugin
from deeppress.classifier_backend_main import predictor


app = None


@hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@route('/classification', method='POST')
def classify_image():
    filename = request.forms.get('model')
    image = request.files.get('image')
    prediction = predictor(image.file.read(), filename)
    if prediction == True:
        return {'success': True, 'Predictions' : prediction}
    else:
        return {'success': False, 'error': 'Could not predict'}


@route('/detection', method='POST')
def detect_objects():
    model = request.forms.get('model')
    image = request.files.get('image')
    thresh = request.forms.get('thresh', default=75, type=int)
    if thresh < 1 or thresh > 99:
        return {'success': False, 'error': "Thresh value should be from 1 to 99"}
    thresh //= 100
    app.load_model(model)
    box = app.detect(image.file.read(), thresh)
    return {'success': True, 'box': box}


@route('/training/status', method="GET")
def get_trainig_status():
    if app.is_training():
        return {'success': True, 'status': app.get_training_status()}
    else:
        return {'success': False}


@route('/training/start', method='POST')
def train_model():
    app.start_training()
    return {'success': True}


@route('/training/stop', method='POST')
def train_model():
    if app.is_training():
        app.stop_training()
    return {'success': True}


def ensure_paths():
    paths = [
        config.TRAINED_MODELS_DATA,
        config.BASE_MODELS_PATH,
        config.EVAL_DIR,
        config.EXPORTED_MODELS,
        config.DATASET_DIR,
        config.TRAIN_DIR,
        config.DOWNLOADS_DIR,
        config.LOG_DIR,
    ]
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)

def main(path=None):
    if path:
        _LOGGER.info("Config path %s", path)

    global app, config
    object.__setattr__(config, '_config', load_config(path))
    ensure_paths()
    app = DeepPressApp()

    install(AuthPlugin(config.LOCAL_AUTH_TOKEN))
    run(host='0.0.0.0', port=8000)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'DeepPress')
    parser.add_argument('--config', help='Config file path')
    args = parser.parse_args()
    main(args.config)


# app.run()