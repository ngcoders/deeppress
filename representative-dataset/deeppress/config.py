import os
import warnings
import codecs
from datetime import timedelta
from urllib.parse import urljoin

from werkzeug.datastructures import ImmutableDict


DEFAULTS = {
    'DEBUG': False,
    'MINIMUM_TRAIN_DATASET': 10,
    'DATA_DIR': '~/deeppress',
    'WP_BASE_URL': "http://localhost",
    'REMOTE_SERVER': True,
    'WP_USERNAME': 'admin',
    'WP_PASSWORD': 'admin',
    'LOCAL_HOST': 'localhost',
    'LOCAL_PORT': 8080,
    'LOCAL_AUTH_TOKEN': 'YWRtaW46YmFzZWFwcA==',

    'NUM_STEPS_FOR_EVAL': 5000,
    'IMAGE_HEIGHT': 640,
    'IMAGE_WIDTH': 640,
    'ADD_QUANTIZATION': False
}


def get_config_path():
    """Get the path of the snms config file.
    This may return the location of a symlink.  Resolving a link is up
    to the caller if needed.
    """
    old_home = os.environ.pop('HOME', None)
    # env var has priority
    try:
        return os.path.expanduser(os.environ['DEEPPRESS_CONFIG'])
    except KeyError:
        pass
    # try finding the config in various common paths
    paths = [os.path.expanduser('~/.deeppress.conf'), '/etc/deeppress.conf']
    # Keeping HOME unset wouldn't be too bad but let's not have weird side-effects
    if old_home is not None:
        os.environ['HOME'] = old_home
    for path in paths:
        if os.path.exists(path):
            return path
    raise Exception('No snms config found. Point the DEEPPRESS_CONFIG env var to your config file or '
                    'move the config in one of the following locations: {}'.format(', '.join(paths)))


def _parse_config(path):
    globals_ = {'timedelta': timedelta}
    locals_ = {}
    with codecs.open(path, encoding='utf-8') as config_file:
        # XXX: unicode_literals is inherited from this file
        exec(compile(config_file.read(), path, 'exec'), globals_, locals_)
    return {str(k if k.isupper() else _convert_key(k)): v
            for k, v in locals_.items()
            if k[0] != '_'}


def _convert_key(name):
    return name


def _postprocess_config(data):
    # data['WP_URL'] = "{}/wp-json/deeppress/v1/records".format(data['WP_BASE_URL'])
    data['WP_URL'] = urljoin(data['WP_BASE_URL'], '/wp-json/deeppress/v1/records')
    # URL for models and groups
    # data['WP_MODULES_URL'] = "{}/wp-json/deeppress/v1".format(data['WP_BASE_URL'])
    data['WP_MODULES_URL'] = urljoin(data['WP_BASE_URL'], '/wp-json/deeppress/v1')

    data['TRAINED_MODELS_DATA'] = os.path.join(data['DATA_DIR'], 'trained_models')
    data['BASE_MODELS_PATH'] = os.path.join(data['DATA_DIR'], 'base_models')
    data['EVAL_DIR'] = os.path.join(data['DATA_DIR'], 'eval_dir')
    data['EXPORTED_MODELS'] = os.path.join(data['DATA_DIR'], 'exported_models')
    data['TFLITE_MODELS'] = os.path.join(data['DATA_DIR'], 'tflite_models')
    data['DATASET_DIR'] = os.path.join(data['DATA_DIR'], 'dataset')
    data['TRAIN_DIR'] = os.path.join(data['DATA_DIR'], 'train')
    data['DOWNLOADS_DIR'] = os.path.join(data['DATA_DIR'], 'downloads')
    data['LOG_DIR'] = os.path.join(data['DATA_DIR'], 'logs')


def _sanitize_data(data, allow_internal=False):
    allowed = set(DEFAULTS)
    # for key in set(data) - allowed:
    #     warnings.warn('Ignoring unknown config key {}'.format(key))
    return {k: v for k, v in data.items() if k in allowed}


def load_config(path=None, override=None):
    """Load the configuration data."""
    data = dict(DEFAULTS)

    if not path:
        path = get_config_path()
    config = _sanitize_data(_parse_config(path))
    data.update(config)
    resolved_path = path
    resolved_path = None if resolved_path == os.devnull else resolved_path
    data['CONFIG_PATH'] = path
    data['CONFIG_PATH_RESOLVED'] = resolved_path

    if override:
        data.update(_sanitize_data(override, allow_internal=True))
    _postprocess_config(data)
    return ImmutableDict(data)


class DeepPressConfig(object):

    __slots__ = ('_config', '_exc')

    def __init__(self, config=None, exc=AttributeError):
        # yuck, but we don't allow writing to attributes directly
        object.__setattr__(self, '_config', config)
        object.__setattr__(self, '_exc', exc)

    @property
    def data(self):
        try:
            return self._config
        except KeyError:
            raise RuntimeError('config not loaded')

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError:
            raise self._exc('no such setting: ' + name)

    def __setattr__(self, key, value):
        raise AttributeError('cannot change config at runtime')

    def __delattr__(self, key):
        raise AttributeError('cannot change config at runtime')


#: The global SNMS configuration
config = DeepPressConfig()
