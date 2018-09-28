import requests
import datetime
import urllib.parse
import json
import os
import queue
import threading
import logging
from tqdm import tqdm

from deeppress import config

from deeppress.config import WP_MODULES_URL, WP_URL

_LOGGER = logging.getLogger('deeppress.api')
_LOGGER.setLevel(logging.DEBUG)
# import tqdm

# Range in data

download_dir = "downloads/"


def get_auth_header():
    """Get Basic Auth for WordPress"""
    return None

class BasePool():
    def __init__(self, num_workers=5):
        self.threads = []
        self.q = queue.Queue()
        self.worker = None
        self.num_workers = num_workers

    def add_task(self, item):
        self.q.put(item)

    def task(self):
        while True:
            item = self.q.get()
            if item is None:
                break
            try:
                self.worker(item)
            except Exception as e:
                _LOGGER.error("Worker Error")
                _LOGGER.error(e)
            self.q.task_done()

    def start(self, worker):
        self.worker = worker
        for i in range(self.num_workers):
            t = threading.Thread(target=self.task)
            t.start()
            self.threads.append(t)

    def join(self):
        self.q.join()
        for i in range(self.num_workers):
            self.q.put(None)
        for t in self.threads:
            t.join()


def get_last_data(group, page=1, per_page=10, extra=None):
    """
    Get latest images from Server.

    :type group: dict Sensor Details
    :param page: int Page number
    :param per_page: int Items per page
    """
    endpoint = WP_URL
    params = {
        'group_id': group['group_id'],
        'page': page,
        'per_page': per_page
    }
    if extra:
        params.update(extra)

    r = requests.get(
        endpoint,
        params=params,
        auth=(config.WP_USERNAME, config.WP_PASSWORD),
        timeout=10
    )
    # _LOGGER.debug(r.text)
    result = r.json()
    # print(result)
    return result


def upload_raw_image(group, _item):
    """
    Upload raw image to the server.

    :param group:
    :param _item:
    :return:
    """
    path = _item['path']
    dt = _item['time']
    batt = _item['batt']
    group_id = group['group_id']

    # t = datetime.datetime.strptime(dt[:-4], "%Y-%m-%dT%H:%M:%S.%f")
    # print(t)
    # created_at = t.isoformat(sep=' ')

    r = requests.post(
        WP_URL, files={
            'image': open(path, 'rb')
        },
        data={
            'group_id': group_id,
            'created_at': dt,
            'batt': batt
        }
    )


def delete_images(records):
    """
    Delete downloaded images.

    :param records: Lest of records
    :return:
    """
    for record in records:
        if record['path'] and os.path.exists(record['path']):
            os.remove(record['path'])


def get_image_by_url(url, location, fname):
    """
    Download an image from  url

    :param url: Image URL
    :param location: Download location
    :param fname: Downloaded file name
    :return: Path of downloaded file
    """
    fname = os.path.join(location, fname)
    if not os.path.exists(fname):
        r = requests.get(url, allow_redirects=True)
        open(fname, 'wb').write(r.content)
        if not os.path.exists(fname):
            return None
    return fname


def get_models(page=1, per_page=10, extra=None):
    """
    Get models from server.

    :return: list of models
    """

    endpoint = "{}/dp_models".format(WP_MODULES_URL)

    return get_module_records(endpoint, page=page, per_page=per_page, extra=extra)


def get_jobs(page=1, per_page=10, extra=None):
    """
    Get models from server.

    :return: list of models
    """

    endpoint = "{}/dp_jobs".format(WP_MODULES_URL)
    return get_module_records(endpoint, page=page, per_page=per_page, extra=extra)


def get_job(id):
    """
    Get models from server.

    :return: list of models
    """

    endpoint = "{}/dp_jobs/{}".format(WP_MODULES_URL, id)
    return get_module_records(endpoint)


def update_model(id, data):
    """
    Update a model

    :param id: Model ID
    :param data: Data to update
    :return:
    """
    endpoint = "{}/dp_models/{}".format(WP_MODULES_URL, id)
    print(endpoint)
    r = requests.post(
            endpoint,
            auth=(config.WP_USERNAME, config.WP_PASSWORD),
            data=data
        )
    _LOGGER.debug(r.text)

def update_job(id, data):
    """
    Update a model

    :param id: Model ID
    :param data: Data to update
    :return:
    """
    endpoint = "{}/dp_jobs/{}".format(WP_MODULES_URL, id)
    r = requests.post(
            endpoint,
            auth=(config.WP_USERNAME, config.WP_PASSWORD),
            data=data
        )
    _LOGGER.debug(r.text)


def update_job_state(job, status, remarks=None, state=None):
    try:
        if remarks:
            d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            job['remarks'] = "{} | {} \n{}".format(d, remarks, job['remarks'][:500])
        data = {'status': status,'remarks': job['remarks']}
        if state:
            data['state'] = state
        update_job(job['id'], data)
    except Exception as e:
        _LOGGER.error(e)
    return job


def get_model(id):
    """
    Get a model

    :param id: Model ID
    :param data: Data to update
    :return:
    """
    endpoint = "{}/dp_models/{}".format(WP_MODULES_URL, id)
    r = requests.get(endpoint, auth=(config.WP_USERNAME, config.WP_PASSWORD))
    _LOGGER.debug(r.text)
    return r.json()


def get_module_records(endpoint, per_page=10, page=1, extra=None):
    """
    Get the module records (models, groups) from server

    :param endpoint: End point for module
    :param per_page: Number of records per page
    :param page: Page number
    :param extra: Extra filters
    :return: List of records
    """
    params = {
        'page': page,
        'per_page': per_page
    }
    if extra:
        params.update(extra)
    # _LOGGER.debug(endpoint)
    r = requests.get(
        endpoint,
        params=params,
        auth=(config.WP_USERNAME, config.WP_PASSWORD),
        timeout=10
    )
    if r.status_code in [401, 403]:
        raise Exception("Auth error with wordpress")
    # _LOGGER.debug(r.text)
    result = r.json()
    # _LOGGER.debug(result)
    return result


def get_groups_list(page=1, per_page=10, extra=None):
    """
    Get list of groups from the server.

    :param page: Page number
    :param per_page: Per page
    :param extra: Extra filters
    :return: List of groups
    """
    endpoint = "{}/dp_groups".format(WP_MODULES_URL)
    return get_module_records(endpoint, page=page, per_page=per_page, extra=extra)


def download_model_files(model_name):
    """
    Download base model checkpoints for a new model

    :param model_name: Name of model
    :return: Downloaded file name
    """
    model_files = {
        'ssd_mobilenet_v1_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_coco_2018_01_28.tar.gz',
            'file_name': 'ssd_mobilenet_v1_coco_2018_01_28.tar.gz'
        },
        'ssd_mobilenet_v2_coco' : {
            'url': 'http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz',
            'file_name': 'ssd_mobilenet_v2_coco_2018_03_29.tar.gz'
        },
        'ssdlite_mobilenet_v2_coco' : {
            'url': 'http://download.tensorflow.org/models/object_detection/ssdlite_mobilenet_v2_coco_2018_05_09.tar.gz',
            'file_name': 'ssdlite_mobilenet_v2_coco_2018_05_09.tar.gz'
        },
        'faster_rcnn_resnet101_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet101_coco_2018_01_28.tar.gz',
            'file_name': 'faster_rcnn_resnet101_coco_2018_01_28.tar.gz'
        },
        'ssd_inception_v2_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/ssd_inception_v2_coco_2018_01_28.tar.gz',
            'file_name': 'ssd_inception_v2_coco_2018_01_28.tar.gz'
        },
        'faster_rcnn_inception_v2_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_v2_coco_2018_01_28.tar.gz',
            'file_name': 'faster_rcnn_inception_v2_coco_2018_01_28.tar.gz'
        },
        'faster_rcnn_resnet50_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet50_coco_2018_01_28.tar.gz',
            'file_name': 'faster_rcnn_resnet50_coco_2018_01_28.tar.gz'
        },
        'faster_rcnn_resnet50_lowproposals_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet50_lowproposals_coco_2018_01_28.tar.gz',
            'file_name': 'faster_rcnn_resnet50_lowproposals_coco_2018_01_28.tar.gz'
        },
        'rfcn_resnet101_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/rfcn_resnet101_coco_2018_01_28.tar.gz',
            'file_name': 'rfcn_resnet101_coco_2018_01_28.tar.gz'
        },
        'faster_rcnn_resnet101_lowproposals_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet101_lowproposals_coco_2018_01_28.tar.gz',
            'file_name': 'faster_rcnn_resnet101_lowproposals_coco_2018_01_28.tar.gz'
        },
        'faster_rcnn_inception_resnet_v2_atrous_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_resnet_v2_atrous_coco_2018_01_28.tar.gz',
            'file_name': 'faster_rcnn_inception_resnet_v2_atrous_coco_2018_01_28.tar.gz'
        },
        'faster_rcnn_inception_resnet_v2_atrous_lowproposals_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_resnet_v2_atrous_lowproposals_coco_2018_01_28.tar.gz',
            'file_name': 'faster_rcnn_inception_resnet_v2_atrous_lowproposals_coco_2018_01_28.tar.gz'
        },
        'faster_rcnn_nas': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_nas_coco_2018_01_28.tar.gz',
            'file_name': 'faster_rcnn_nas_coco_2018_01_28.tar.gz'
        },
        'faster_rcnn_nas_lowproposals_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_nas_lowproposals_coco_2018_01_28.tar.gz',
            'file_name': 'faster_rcnn_nas_lowproposals_coco_2018_01_28.tar.gz'
        },
        'mask_rcnn_inception_resnet_v2_atrous_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/mask_rcnn_inception_resnet_v2_atrous_coco_2018_01_28.tar.gz',
            'file_name': 'mask_rcnn_inception_resnet_v2_atrous_coco_2018_01_28.tar.gz'
        },
        'mask_rcnn_inception_v2_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/mask_rcnn_inception_v2_coco_2018_01_28.tar.gz',
            'file_name': 'mask_rcnn_inception_v2_coco_2018_01_28.tar.gz'
        },
        'mask_rcnn_resnet101_atrous_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/mask_rcnn_resnet101_atrous_coco_2018_01_28.tar.gz',
            'file_name': 'mask_rcnn_resnet101_atrous_coco_2018_01_28.tar.gz'
        },
	    'mask_rcnn_resnet50_atrous_coco': {
            'url': 'http://download.tensorflow.org/models/object_detection/mask_rcnn_resnet50_atrous_coco_2018_01_28.tar.gz',
            'file_name': 'mask_rcnn_resnet50_atrous_coco_2018_01_28.tar.gz'
        },
        'faster_rcnn_resnet101_kitti': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet101_kitti_2018_01_28.tar.gz',
            'file_name': 'faster_rcnn_resnet101_kitti_2018_01_28.tar.gz'
        },
        'faster_rcnn_inception_resnet_v2_atrous_oid': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_resnet_v2_atrous_oid_2018_01_28.tar.gz',
            'file_name': 'faster_rcnn_inception_resnet_v2_atrous_oid_2018_01_28.tar.gz'
        },
        'faster_rcnn_inception_resnet_v2_atrous_lowproposals_oid': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_resnet_v2_atrous_lowproposals_oid_2018_01_28.tar.gz',
            'file_name': 'faster_rcnn_inception_resnet_v2_atrous_lowproposals_oid_2018_01_28.tar.gz'
        },
        'faster_rcnn_resnet101_ava_v2.1': {
            'url': 'http://download.tensorflow.org/models/object_detection/faster_rcnn_resnet101_ava_v2.1_2018_04_30.tar.gz',
            'file_name': 'faster_rcnn_resnet101_ava_v2.1_2018_04_30.tar.gz'
        }
    }
    if not model_name in model_files.keys():
        return None

    if os.path.exists(model_files[model_name]['file_name']):
        return model_files[model_name]['file_name']

    r = requests.get(model_files[model_name]['url'], allow_redirects=True)
    with open(model_files[model_name]['file_name'], 'wb') as _f:
        _f.write(r.content)
    if not os.path.exists(model_files[model_name]['file_name']):
        return None
    return model_files[model_name]['file_name']


def mark_trained(ids):
    """Mark images as trained"""
    r = requests.post(
            "{}/0/trained".format(WP_URL),
            data={
                'ids[]': ids
            },
            auth=(config.WP_USERNAME, config.WP_PASSWORD)
        )
    if r.status_code != 200:
        _LOGGER.debug(r.text)


def get_classes(page=1, per_page=500, extra=None):
    """Get object classes"""
    endpoint = "{}/dp_classes".format(WP_MODULES_URL)
    return get_module_records(endpoint, page=page, per_page=per_page, extra=extra)

if __name__ == "__main__":
    pass
