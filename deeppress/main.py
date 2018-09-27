import sys
import logging

# from trainer import TrainingApp
from deeppress.app import DeepPressApp
from deeppress.bottle import install, route, run, request, hook, response
from deeppress.web import AuthPlugin
import deeppress.config as config


_LOGGER = logging.getLogger('deeppress')
_LOGGER.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
_LOGGER.addHandler(ch)

install(AuthPlugin(config.LOCAL_AUTH_TOKEN))
app = DeepPressApp()

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
    thresh = float(request.forms.get('thresh'))
    app.load_model(model)
    box = app.detect(image.file.read(), thresh)
    return {'success': True, 'box': box}

run(host='localhost', port=8080)

# app.run()