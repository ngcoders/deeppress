import sys
import logging
import argparse

# from trainer import TrainingApp
from deeppress.app import DeepPressApp
from deeppress.bottle import install, route, run, request, hook, response
from deeppress.web import AuthPlugin
from deeppress.config import config, load_config, DeepPressConfig


_LOGGER = logging.getLogger('deeppress')
_LOGGER.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
_LOGGER.addHandler(ch)

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


@route('/classify')
def classify_image():
    return "Not implemented yet"


@route('/detect', method='POST')
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


def main(path=None):
    if path:
        _LOGGER.info("Config path %s", path)

    global app, config
    object.__setattr__(config, '_config', load_config(path))
    app = DeepPressApp()

    install(AuthPlugin(config.LOCAL_AUTH_TOKEN))
    run(host='localhost', port=8080)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'DeepPress')
    parser.add_argument('--config', help='Config file path')
    args = parser.parse_args()
    main(args.config)


# app.run()