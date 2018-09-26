import sys
import logging

from trainer import TrainingApp
from bottle import install
from web import AuthPlugin
import config


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
app = TrainingApp()
app.register_routes()
app.run()