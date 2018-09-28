import functools
from multiprocessing import Process
import sys
import logging
import os
from tqdm import tqdm
import json
import tarfile
import shutil
import tensorflow as tf
from tensorflow.python.lib.io import file_io
from datetime import datetime
import re

from object_detection import trainer
from object_detection.builders import dataset_builder
from object_detection.builders import graph_rewriter_builder
from object_detection.builders import model_builder
from object_detection.utils import config_util


from deeppress import api
from deeppress.image_to_tfr import TFRConverter
from deeppress import exporter
from deeppress.eval import run_eval
from deeppress.config import config
from deeppress.utils import TFLogHandler, StatusThread
from deeppress import label_maker

_LOGGER = logging.getLogger('deeppress.job')

tfh = TFLogHandler()
tfl = logging.getLogger('tensorflow').addHandler(tfh)


def ensure_path(path_name):
    if not os.path.exists(path_name):
        tf.gfile.MakeDirs(path_name)


def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


class TrainingJob(Process):
    def __init__(self, job):
        """Start a new training Job"""
        super(TrainingJob, self).__init__()
        self.job = job
        self.model = None
        self.groups = []
        self.data_dir = None
        self.status = {
            "status": "created",
            "ETA": None,
            "job": job
        }
        self.configs_dir = os.path.join(os.path.dirname(__file__), "configs")
        self.train_dir = '{}/job_{}'.format(config.TRAIN_DIR, self.job['id'])
        ensure_path(self.train_dir)
        # If pipeline config file already there.
        self.already_running = os.path.isfile(os.path.join(self.train_dir, 'pipeline.config'))

    def get_status(self):
        return self.status

    def update_status(self, key, value):
        try:
            self.status[key] = value
        except KeyError:
            pass
        except Exception as e:
            _LOGGER.error(e)

    def run(self):
        self.get_model()
        self.get_groups()
        # TODO: If job is already exists
        if self.already_running or self.prepare_dataset():
            if self.start_training():
                self.cleanup()
                api.update_model(self.model['id'],
                         {
                             'last_trained': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                         })
                api.update_job(self.job['id'], {'done': 1})

    def get_model(self):
        model_id = self.job['model']
        _model = api.get_model(model_id)
        if _model:
            file_name = _model['file_name'].strip()
            if len(file_name) == 0:
                file_name = "{}_{}".format(_model['architecture'], _model['id'])

            file_name = get_valid_filename(file_name)

            if file_name != _model['file_name']:
                _model['file_name'] = file_name
                api.update_model(_model['id'], {'file_name': file_name})

            self.model = _model
            self.data_dir = os.path.join(config.DATASET_DIR, _model['file_name'])
            ensure_path(self.data_dir)
        else:
            raise Exception("Model not found")

    def get_groups(self):
        if type(self.job['groups']) is list:
            self.groups = self.job['groups']
        else:
            self.groups = []
        return

        # model_id = self.model["id"]
        # page = 1
        # while True:
        #     res = api.get_groups_list(page=page, per_page=50)
        #     if isinstance(res, dict) and 'data' in res.keys():
        #         data = res['data']
        #         total = res['total']
        #         page += 1
        #         if len(data) == 0:
        #             break
        #         for record in data:
        #             group_model_id = int(record['model'])
        #             if model_id != 0 and int(model_id) == group_model_id:
        #                 self.groups.append(record['group_id'])

    def cleanup(self):
        """Clean all the model related data"""
        shutil.rmtree(self.data_dir)

    def prepare_dataset(self):
        """Prepare dataset for training"""
        model = self.model

        def downloader(record):
            api.get_image_by_url(record['url'], "", record["path"])

        self.data_dir = os.path.join(config.DATASET_DIR, model['file_name'])
        ensure_path(self.data_dir)

        labels_file = "{}/labels.pbtxt".format(self.data_dir)

        label_maker.make(labels_file)

        with TFRConverter(self.data_dir, labels_file=labels_file) as tf_converter:
            for group in self.groups:
                _LOGGER.debug("Loading images for group %s" % group)
                page = 1
                bar = None
                while True:
                    res = api.get_last_data({'group_id': group}, extra={'annotated': 1, 'page': page, 'trained': 0})
                    if isinstance(res, dict) and 'data' in res.keys():
                        images = res['data']
                        if len(images) == 0:  # No more images to download
                            break
                        if not bar:
                            bar = tqdm(total = res['total'])
                        trained_images = []
                        images_folder = config.DOWNLOADS_DIR
                        ensure_path(images_folder)
                        if config.REMOTE_SERVER:
                            pool = api.BasePool(10)
                            pool.start(downloader)
                            for image in images:
                                url = image['image']
                                if url.startswith('/wp-content'):
                                    url = config.WP_BASE_URL + url
                                image['image_file'] = os.path.join(images_folder, 'image_{}.jpeg'.format(image['id']))

                                pool.add_task({"url": url, 'path': image['image_file']})

                            pool.join()

                        for image in images:
                            if bar:
                                bar.update(1)

                            image_path = image['image_file']
                            if not os.path.exists(image_path):
                                image_path = None
                            if not image_path:
                                _LOGGER.error("failed to download image %s" % image['image'])
                                continue

                            # _LOGGER.debug(image['box'])
                            try:
                                boxes = json.loads(image['box'])
                            except Exception as e:
                                _LOGGER.error("JSON Deserialize Error")
                                _LOGGER.error(e)
                                continue
                            # _LOGGER.debug("{} box in image".format(len(boxes)))

                            trained_images.append(image['id'])
                            tf_converter.add_record(image_path, boxes)

                            # NOTE: Delete local image if downloaded from server
                            if config.REMOTE_SERVER:
                                if os.path.exists(image_path):
                                    os.remove(image_path)

                        api.mark_trained(trained_images)
                        trained_images = []
                        # page += 1
                    else:
                        _LOGGER.error("Invalid response from server")
                        break
                    # break
                if bar:
                    bar.close()

            stats = tf_converter.counts
            msg = "Dataset:- Train : {}, Test : {}".format(stats['train'], stats['test'])
            _LOGGER.info(msg)
            model = api.update_job_state(self.job, 'running', msg)
            model = api.update_job_state(self.job, 'running', 'Preparing dataset complete')

            # TODO: Check for minimum requirements for train test data
            if stats['train'] < config.MINIMUM_TRAIN_DATASET:
                _LOGGER.info("Minimum images required for training")
                model = api.update_job_state(self.job, 'error', 'Dataset not enough for training')
                return False
            else:
                return True

    @classmethod
    def get_existing_job(cls):
        train_dir = 'models'
        model_json_path = os.path.join(train_dir, 'job.json')
        if os.path.exists(model_json_path):
            _LOGGER.info("Model details found in, loading existing model")
            with open(model_json_path) as mf:
                job = json.load(mf)
                return cls(job)
        else:
            return None

    def start_training(self):
        """Start training for the model"""
        worker_replicas = 1
        ps_tasks = 0
        clone_on_cpu = False
        num_clones = 1

        ensure_path(config.BASE_MODELS_PATH)
        train_dir = self.train_dir
        model_json_path = os.path.join(train_dir, 'job.json')

        job = self.job
        num_steps = int(job['steps'])

        try:
            if config.DEBUG:
                num_steps = 50
        except AttributeError:
            pass
        except Exception as e:
            _LOGGER.error(e)

        job = api.update_job_state(job, 'training', 'Start training for {} steps'.format(num_steps))

        model = self.model
        ensure_path(config.EXPORTED_MODELS)
        model_graph = os.path.join(config.EXPORTED_MODELS, '{}.pb'.format(model['file_name']))

        if not os.path.exists(os.path.join(train_dir, 'checkpoint')):  # New training started
            _LOGGER.debug("Checkpoints doesn't exists")

            base_checkpoints_path = os.path.join(config.BASE_MODELS_PATH, model['architecture'])
            _tmf = os.path.join(config.TRAINED_MODELS_DATA, model['file_name'])
            if os.path.isdir(_tmf):
                _LOGGER.debug("Model already exists as %s" % model_graph)
                base_checkpoints_path = _tmf
            elif model['type'] == 'new':
                _LOGGER.debug("model type new")
            else:
                _LOGGER.debug("New model from parent model")
                parent_model = api.get_model(model['parent'])
                if not parent_model:
                    raise Exception('Parent model not found on server')

                parent_tmf = os.path.join(config.TRAINED_MODELS_DATA, parent_model['file_name'])
                if os.path.isdir(parent_tmf):
                    base_checkpoints_path = parent_tmf
                else:
                    _LOGGER.error("Parent model not found. please train it first")
                    return False

            if not os.path.exists(os.path.join(base_checkpoints_path, 'model.ckpt.meta')):
                _LOGGER.debug("Base model not found for %s, Downloading now." % model['architecture'])
                _f = api.download_model_files(model['architecture'])

                tmp_model_data = os.path.join(config.DATA_DIR, 'tmp_model_data')
                if tarfile.is_tarfile(_f):
                    if os.path.exists(tmp_model_data):
                        shutil.rmtree(tmp_model_data)
                    ensure_path(tmp_model_data)
                    print("Tar file found")
                    shutil.unpack_archive(_f, tmp_model_data)
                    for root, dirs, files in os.walk(tmp_model_data):
                        for file in files:
                            if 'model.ckpt' in file:
                                path = os.path.join(root, file)
                                # print(path)
                                ensure_path(base_checkpoints_path)
                                shutil.copy(path, os.path.join(base_checkpoints_path, file))
                else:
                    _LOGGER.error("Invalid file")
                    return False
            if os.path.exists(train_dir):
                shutil.rmtree(train_dir)
            shutil.copytree(base_checkpoints_path, train_dir)
            if os.path.exists(os.path.join(train_dir, 'checkpoint')):
                os.remove(os.path.join(train_dir, 'checkpoint'))

        if os.path.exists(os.path.join(train_dir, 'data')):
            shutil.rmtree(os.path.join(train_dir, 'data'))
        shutil.copytree(os.path.join('data', model['file_name']), os.path.join(train_dir, 'data'))

        counts = {'train': 0, 'test': 1000, 'classes': 1}
        stats_file = os.path.join(train_dir, "data", "stats.json")
        try:
            with open(stats_file) as _f:
                counts = json.load(_f)
        except:
            pass

        pipeline_config_path = os.path.join(train_dir, 'pipeline.config')
        if not os.path.exists(pipeline_config_path):
            pipeline_config_path = os.path.join(self.configs_dir, "{}.config".format(model['architecture']))
        task = '0'
        if task == '0':
            tf.gfile.MakeDirs(train_dir)
        if pipeline_config_path:
            _LOGGER.info("Pipeline config file : {}".format(pipeline_config_path))
            configs = config_util.get_configs_from_pipeline_file(
                pipeline_config_path)
            if task == '0':
                tf.gfile.Copy(pipeline_config_path,
                              os.path.join(train_dir, 'pipeline.config'),
                              overwrite=True)
        else:
            _LOGGER.error("No config found")
            return False

        pipeline_config_path = os.path.join(train_dir, 'pipeline.config')

        # with open(model_json_path, 'w') as mf:
        #     json.dump(job, mf)

        model_config = configs['model']
        train_config = configs['train_config']
        input_config = configs['train_input_config']


        if model_config.HasField('faster_rcnn'):
            model_config.faster_rcnn.num_classes = counts['classes']

        if model_config.HasField('ssd'):
            model_config.ssd.num_classes = counts['classes']

        # Set num_steps
        train_config.num_steps = num_steps
        train_config.fine_tune_checkpoint = os.path.join(train_dir, 'model.ckpt')

        # Update input config to use updated list of input
        input_config.tf_record_input_reader.ClearField('input_path')
        input_config.tf_record_input_reader.input_path.append(os.path.join(train_dir, 'data', "train_baheads.tfrecord-??????"))
        input_config.label_map_path = os.path.join(train_dir, 'data', "labels.pbtxt")

        eval_config = configs['eval_config']
        eval_input_config = configs['eval_input_config']

        eval_config.num_examples = counts['test']
        eval_config.max_evals = 1

        # Update input config to use updated list of input
        eval_input_config.tf_record_input_reader.ClearField('input_path')
        eval_input_config.tf_record_input_reader.input_path.append(os.path.join(train_dir, 'data', "test_baheads.tfrecord-??????"))
        eval_input_config.label_map_path = os.path.join(train_dir, 'data', "labels.pbtxt")

        # Save the updated config to pipeline file
        config_util.save_pipeline_config(config_util.create_pipeline_proto_from_configs({
            'model': model_config,
            'train_config': train_config,
            'train_input_config': input_config,
            'eval_config': eval_config,
            'eval_input_config': eval_input_config

        }), train_dir)

        model_fn = functools.partial(
            model_builder.build,
            model_config=model_config,
            is_training=True)

        def get_next(config):
            return dataset_builder.make_initializable_iterator(
                dataset_builder.build(config)).get_next()

        create_input_dict_fn = functools.partial(get_next, input_config)

        env = json.loads(os.environ.get('TF_CONFIG', '{}'))
        cluster_data = env.get('cluster', None)
        cluster = tf.train.ClusterSpec(cluster_data) if cluster_data else None
        task_data = env.get('task', None) or {'type': 'master', 'index': 0}
        task_info = type('TaskSpec', (object,), task_data)

        # Parameters for a single worker.
        ps_tasks = 0
        worker_replicas = 1
        worker_job_name = 'lonely_worker'
        task = 0
        is_chief = True
        master = ''

        if cluster_data and 'worker' in cluster_data:
            # Number of total worker replicas include "worker"s and the "master".
            worker_replicas = len(cluster_data['worker']) + 1
        if cluster_data and 'ps' in cluster_data:
            ps_tasks = len(cluster_data['ps'])

        if worker_replicas > 1 and ps_tasks < 1:
            raise ValueError('At least 1 ps task is needed for distributed training.')

        if worker_replicas >= 1 and ps_tasks > 0:
            # Set up distributed training.
            server = tf.train.Server(tf.train.ClusterSpec(cluster), protocol='grpc',
                                     job_name=task_info.type,
                                     task_index=task_info.index)
            if task_info.type == 'ps':
                server.join()
                return

            worker_job_name = '%s/task:%d' % (task_info.type, task_info.index)
            task = task_info.index
            is_chief = (task_info.type == 'master')
            master = server.target

        graph_rewriter_fn = None
        if 'graph_rewriter_config' in configs:
            graph_rewriter_fn = graph_rewriter_builder.build(
                configs['graph_rewriter_config'], is_training=True)

        if not os.path.exists(os.path.join(train_dir, 'model.ckpt-{}.meta'.format(num_steps))):
            status_timer = StatusThread(tfh, num_steps, job)
            status_timer.start()
            try:
                trainer.train(
                    create_input_dict_fn,
                    model_fn,
                    train_config,
                    master,
                    task,
                    num_clones,
                    worker_replicas,
                    clone_on_cpu,
                    ps_tasks,
                    worker_job_name,
                    is_chief,
                    train_dir,
                    graph_hook_fn=graph_rewriter_fn)
            except KeyboardInterrupt:
                raise
            finally:
                status_timer.stop()
                if status_timer.is_alive():
                    _LOGGER.info("Waiting for status thread to close")
                    status_timer.join()

        if os.path.exists(os.path.join(train_dir, 'model.ckpt-{}.meta'.format(num_steps))):
            # Training complete. Export model
            _LOGGER.debug("Training complete for %d steps" % num_steps)
            job = api.update_job_state(job, 'training', 'Training complete')
            export_path = os.path.join(config.TRAINED_MODELS_DATA, model['file_name'])
            if os.path.exists(export_path):
                shutil.rmtree(export_path)
            ckpt_path = os.path.join(train_dir, 'model.ckpt-{}'.format(num_steps))
            exporter.export(pipeline_config_path, export_path, ckpt_path)

            frozen_graph = os.path.join(export_path, 'frozen_inference_graph.pb')

            if os.path.exists(frozen_graph):  # Successfully exported
                shutil.copy(frozen_graph, model_graph)
                shutil.copy(
                    os.path.join(train_dir, 'data', "labels.pbtxt"),
                    os.path.join(config.EXPORTED_MODELS, '{}.pbtxt'.format(model['file_name']))
                )
                # TODO: Eval the trained graph, Push the result to server.
                eval_dir = 'eval_dir'
                tf.reset_default_graph()
                eval_result = run_eval(train_dir, eval_dir, pipeline_config_path, counts['test'])
                if 'PascalBoxes_Precision/mAP@0.5IOU' in eval_result:
                    acc = eval_result['PascalBoxes_Precision/mAP@0.5IOU'] * 100
                    _LOGGER.info("PascalBoxes_Precision/mAP@0.5IOU : %d %%" % (acc))
                    job = api.update_job_state(job, 'complete', 'PascalBoxes_Precision %d %%' % (acc))
                _LOGGER.info(eval_result)
                if os.path.exists(train_dir):
                    shutil.rmtree(train_dir)
                return True

        return False
