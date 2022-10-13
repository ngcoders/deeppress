import contextlib
import glob
import functools
from multiprocessing import Process
import sys
import logging
import os
from tqdm import tqdm
import json
import tarfile
import shutil
import subprocess
from threading import Thread

from datetime import datetime
import re
import tensorflow as tf
from object_detection.utils import config_util

from deeppress import api
from deeppress.image_to_tfr import TFRConverter
from deeppress import exporter
from deeppress.config import config
from deeppress.utils import TailThread
from deeppress import label_maker


tfl = logging.getLogger('tensorflow')
tfl.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='%(levelname).1s %(asctime)s.%(msecs).03d: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
for h in tfl.handlers:
    h.setFormatter(formatter)
_LOGGER = logging.getLogger('deeppress.job')
tfl.addHandler(_LOGGER)
tfl.propagate = False


quant = '''
graph_rewriter {
  quantization {
    delay: 48000
    weight_bits: 8
    activation_bits: 8
  }
}
'''


def ensure_path(path_name):
    if not os.path.exists(path_name):
        tf.io.gfile.makedirs(path_name)


def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


class EditPipeline():
    ''' 
        this class contains pipeline edit functions for each type of model.
        use it as a inheritance to the TrainingJob class.
    '''
    def __init__(self):
        pass

    def faster_rcnn_replicating_humandetection_v2_1(self, job, model_config, train_config, counts):
        model_config.faster_rcnn.num_classes = counts
        model_config.faster_rcnn.image_resizer.fixed_shape_resizer.height = 600
        model_config.faster_rcnn.image_resizer.fixed_shape_resizer.width = 800
        # model_config.faster_rcnn.image_resizer.keep_aspect_ratio_resizer.min_dimension = 600
        # model_config.faster_rcnn.image_resizer.keep_aspect_ratio_resizer.max_dimension = 1024
        
        train_config.batch_size = 1
        train_config.optimizer.momentum_optimizer.learning_rate.manual_step_learning_rate.initial_learning_rate = 0.00030000001

        train_config.optimizer.momentum_optimizer.learning_rate.manual_step_learning_rate.schedule.add()
        train_config.optimizer.momentum_optimizer.learning_rate.manual_step_learning_rate.schedule[0].step = 900000
        train_config.optimizer.momentum_optimizer.learning_rate.manual_step_learning_rate.schedule[0].learning_rate = 2.9999999e-05
        train_config.optimizer.momentum_optimizer.learning_rate.manual_step_learning_rate.schedule.add()
        train_config.optimizer.momentum_optimizer.learning_rate.manual_step_learning_rate.schedule[1].step = 1200000
        train_config.optimizer.momentum_optimizer.learning_rate.manual_step_learning_rate.schedule[1].learning_rate = 3.0000001e-06

    def faster_rcnn(self, job, model_config, train_config, counts):
        ''' configurations specific for faster_rcnn ''' 
        model_config.faster_rcnn.num_classes = counts
        model_config.faster_rcnn.image_resizer.fixed_shape_resizer.height = config.IMAGE_HEIGHT
        model_config.faster_rcnn.image_resizer.fixed_shape_resizer.width = config.IMAGE_WIDTH
        # model_config.faster_rcnn.image_resizer.keep_aspect_ratio_resizer.min_dimension = 600
        # model_config.faster_rcnn.image_resizer.keep_aspect_ratio_resizer.max_dimension = 1024
        try:
            learning_rate = job['learning_rate']
        except Exception:
            learning_rate = 0.000159
        train_config.batch_size = 2
        train_config.optimizer.momentum_optimizer.learning_rate.cosine_decay_learning_rate.learning_rate_base = learning_rate
        train_config.optimizer.momentum_optimizer.learning_rate.cosine_decay_learning_rate.total_steps = self.endStep
        train_config.optimizer.momentum_optimizer.learning_rate.cosine_decay_learning_rate.warmup_learning_rate = learning_rate / 10
        train_config.optimizer.momentum_optimizer.learning_rate.cosine_decay_learning_rate.warmup_steps = int(self.endStep / 20)

    def efficientdet(self, job, model_config, train_config, counts):
        ''' configurations specific for efficientdet ''' 
        model_config.ssd.num_classes = counts
        # model_config.ssd.image_resizer.fixed_shape_resizer.height = config.IMAGE_HEIGHT
        # model_config.ssd.image_resizer.fixed_shape_resizer.width = config.IMAGE_WIDTH
        # model_config.ssd.image_resizer.keep_aspect_ratio_resizer.min_dimension = 768
        # model_config.ssd.image_resizer.keep_aspect_ratio_resizer.max_dimension = 768
        # model_config.ssd.image_resizer.keep_aspect_ratio_resizer.pad_to_max_dimension = True

        try:
            learning_rate = job['learning_rate']
        except Exception:
            learning_rate = 0.00025
        train_config.batch_size = 2
        train_config.optimizer.adam_optimizer.learning_rate.exponential_decay_learning_rate.initial_learning_rate = learning_rate
        train_config.optimizer.adam_optimizer.learning_rate.exponential_decay_learning_rate.decay_steps = int(self.endStep / 5)

    def ssd(self, job, model_config, train_config, counts):
        ''' configurations specific for ssd '''
        model_config.ssd.num_classes = counts
        # if not self.job['add_quantization']:
        #     model_config.ssd.image_resizer.keep_aspect_ratio_resizer.min_dimension = config.IMAGE_HEIGHT
        #     model_config.ssd.image_resizer.keep_aspect_ratio_resizer.max_dimension = config.IMAGE_WIDTH
        #     model_config.ssd.image_resizer.keep_aspect_ratio_resizer.pad_to_max_dimension = True
        # else:
        #     the tflite needs the height and width to be the same (as in the original pipeline.config)
        #     so do not change it
        #     model_config.ssd.image_resizer.fixed_shape_resizer.height = config.IMAGE_HEIGHT
        #     model_config.ssd.image_resizer.fixed_shape_resizer.width = config.IMAGE_WIDTH

        try:
            learning_rate = job['learning_rate']
        except Exception:
            learning_rate = 0.000159
        train_config.batch_size = 4
        # train_config.optimizer.adam_optimizer.learning_rate.exponential_decay_learning_rate.initial_learning_rate = learning_rate
        # train_config.optimizer.adam_optimizer.learning_rate.exponential_decay_learning_rate.decay_steps = int(self.endStep / 4)
        train_config.optimizer.momentum_optimizer.learning_rate.cosine_decay_learning_rate.learning_rate_base = learning_rate
        train_config.optimizer.momentum_optimizer.learning_rate.cosine_decay_learning_rate.total_steps = self.endStep
        train_config.optimizer.momentum_optimizer.learning_rate.cosine_decay_learning_rate.warmup_learning_rate = learning_rate / 10
        train_config.optimizer.momentum_optimizer.learning_rate.cosine_decay_learning_rate.warmup_steps = int(self.endStep / 100)
        train_config.optimizer.momentum_optimizer.momentum_optimizer_value = 0.9
        train_config.optimizer.use_moving_average: False

    def edit_pipeline(self, job, model, counts):
        ''' edit the pipeline '''
        train_dir = self.train_dir
        base_model_pipeline = os.path.join(config.BASE_MODELS_PATH, self.model['architecture'], 'pipeline.config')
        self.pipeline_config_path = os.path.join(train_dir, 'pipeline.config')
        job['pipeline_config_path'] = self.pipeline_config_path
        if not os.path.exists(base_model_pipeline):
            raise FileNotFoundError(f'pipeline file does not exists in {base_model_pipeline}')

        shutil.copyfile(base_model_pipeline, self.pipeline_config_path)

        configs = config_util.get_configs_from_pipeline_file(self.pipeline_config_path)
        model_config = configs['model']
        train_config = configs['train_config']
        input_config = configs['train_input_config']

        if model_config.HasField('faster_rcnn'):
            self.faster_rcnn(job, model_config, train_config, counts['classes'])
        elif 'efficientdet' in model['architecture']:
            self.efficientdet(job, model_config, train_config, counts['classes'])
        elif model_config.HasField('ssd'):
            self.ssd(job, model_config, train_config, counts['classes'])

        # Set num_steps
        train_config.num_steps = self.trainSteps
        train_config.fine_tune_checkpoint = job['checkpoint']
        train_config.fine_tune_checkpoint_type = 'detection'

        # Update input config to use updated list of input
        input_config.tf_record_input_reader.ClearField('input_path')
        input_config.tf_record_input_reader.input_path.append(os.path.join(train_dir, 'data', "train_baheads.tfrecord-*"))
        input_config.label_map_path = self.labels_file

        eval_config = configs['eval_config']
        eval_input_config = configs['eval_input_configs'][0]

        eval_config.num_examples = counts['test']
        eval_config.max_evals = 1

        # Update input config to use updated list of input
        eval_input_config.shuffle = True
        eval_input_config.tf_record_input_reader.ClearField('input_path')
        eval_input_config.tf_record_input_reader.input_path.append(os.path.join(train_dir, 'data', "test_baheads.tfrecord-*"))
        eval_input_config.label_map_path = self.labels_file

        # if job['add_quantization']:
        #     # add quatization parameters
        #     configs['graph_rewriter'].quantization.delay = 48000
        #     configs['graph_rewriter'].quantization.weight_bits = 8
        #     configs['graph_rewriter'].quantization.activation_bits = 8

        # Save the updated config to pipeline file
        config_util.save_pipeline_config(config_util.create_pipeline_proto_from_configs({
            'model': model_config,
            'train_config': train_config,
            'train_input_config': input_config,
            'eval_config': eval_config,
            'eval_input_configs': [eval_input_config]
        }), train_dir)

        # if self.job['add_quantization']:
            # global quant
            # with open(self.pipeline_config_path, 'a') as handle:
            #     handle.write(quant)
        return True


class TrainEvalWorkAround():
    ''' 
        this is a work around to run train and eval simultaneously in object detection tf2.
        use it as an inheritance to the TrainingJob class.
    '''
    def __init__(self, job):
        pass

    def update_pipeline(self, train_dir, num_train_steps):
        ''' updates the pipeline file for each training and evaluation '''
        configs = config_util.get_configs_from_pipeline_file(self.pipeline_config_path)
        model_config = configs['model']
        train_config = configs['train_config']
        input_config = configs['train_input_config']

        # Set num_steps
        train_config.num_steps = num_train_steps
        train_config.fine_tune_checkpoint = tf.train.latest_checkpoint(os.path.join(train_dir, 'checkpoint_dir'))

        eval_config = configs['eval_config']
        eval_input_config = configs['eval_input_configs'][0]

        # Save the updated config to pipeline file
        config_util.save_pipeline_config(
            config_util.create_pipeline_proto_from_configs
            ({
                'model': model_config,
                'train_config': train_config,
                'train_input_config': input_config,
                'eval_config': eval_config,
                'eval_input_configs': [eval_input_config]
            }), train_dir)
        return True

    def copy_ckpt(self, train_dir):
        ''' copy the latest checkpoint to another folder to start the next training '''
        '''
            In order to mitigate "RuntimeError: Checkpoint dir and model_dir cannot be same.
            Please set model_dir to a different path." error in tensorflow 2.
        '''
        fine_tune_checkpoint = tf.train.latest_checkpoint(train_dir)
        checkpoint_dir = os.path.join(train_dir, 'checkpoint_dir')
        if os.path.exists(checkpoint_dir):
            shutil.rmtree(checkpoint_dir)
        os.makedirs(checkpoint_dir)

        # copy the ckpt-<index>* file
        for filename in glob.glob(f'{fine_tune_checkpoint}*'):
            shutil.copy(filename, checkpoint_dir)

        # copy the checkpoint file
        shutil.copy(os.path.join(train_dir, 'checkpoint'), checkpoint_dir)
        return os.path.join(checkpoint_dir, os.path.basename(fine_tune_checkpoint))

    def check_training(self, index, train_dir):
        ''' check if the checkpoint file is created ''' 
        latest_checkpoint = tf.train.latest_checkpoint(train_dir)
        desired_checkpoint = os.path.join(train_dir, f'ckpt-{index+2}')
        if latest_checkpoint == desired_checkpoint:
            return True
        _LOGGER.error(f'Trained checkpoint {desired_checkpoint} not found')
        return False

    def train_and_eval(self, job):
        ''' run train and eval ''' 
        time_str = datetime.now().strftime('%y%m%d_%H%M%S')
        logger_filename_train = os.path.join(config.LOG_DIR, f"job_{job['id']}_{time_str}_train")
        logger_filename_test = os.path.join(config.LOG_DIR, f"job_{job['id']}_{time_str}_test")
        physical_devices = tf.config.list_physical_devices('GPU')
        for gpu_instance in physical_devices: 
            tf.config.experimental.set_memory_growth(gpu_instance, True)
        startStep = 0
        endStep = self.endStep
        evalStep = self.evalStep
        firstrun = True
        for index, num_train_steps in enumerate(range(startStep + evalStep, endStep + 1, evalStep)):
            # if num_train_steps == evalStep:
            if firstrun:
                firstrun = False
            else:
                # copy the ckpt and edit the pipeline if it is not the first step
                self.copy_ckpt(self.train_dir)
                self.update_pipeline(self.train_dir, num_train_steps)
            print(f'***** \n\n start _train {num_train_steps}/{endStep} \n\n***')
            process_train = Process(target=self._train, args=(job, logger_filename_train))
            process_train.start()
            process_train.join()
            if not self.check_training(index, self.train_dir):
                return False
            print(f'***** \n\n start _eval {num_train_steps}/{endStep} \n\n***')
            process_eval = Process(target=self._eval, args=(job, logger_filename_test))
            process_eval.start()
            process_eval.join()
        return True
    

class TrainingJob(Process, TrainEvalWorkAround, EditPipeline):
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
        self.train_dir = os.path.join(config.TRAIN_DIR, f"job_{self.job['id']}")
        ensure_path(self.train_dir)
        # If pipeline config file already there.
        self.already_running = os.path.isfile(os.path.join(self.train_dir, 'pipeline.config'))

        physical_devices = tf.config.list_physical_devices('GPU')
        for gpu_instance in physical_devices: 
            tf.config.experimental.set_memory_growth(gpu_instance, True)

    def init_params(self):
        ''' initialize the parameters for the training '''
        ensure_path(self.train_dir)
        self.data_dir = os.path.join(config.DATASET_DIR, self.model['file_name'])
        ensure_path(self.data_dir)
        ensure_path(config.EXPORTED_MODELS)
        # labels_file initially made in the data_dir and copied to data/train/data directory
        self.labels_file = os.path.join(self.data_dir, 'labels.pbtxt')

        self.job['add_quantization'] = bool(config.ADD_QUANTIZATION)
        self.job['tfliteDir'] = os.path.join(config.TFLITE_MODELS, self.model['file_name'])

        self.endStep = int(self.job['steps'])
        # self.trainSteps = int(self.job['steps'])                           # for continues training
        self.trainSteps = min(config.NUM_STEPS_FOR_EVAL, self.endStep)     # for train and eval
        self.startStep = 0
        self.evalStep = min(config.NUM_STEPS_FOR_EVAL, self.endStep)

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
        self.init_params()
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
        else:
            raise Exception("Model not found")

    def get_groups(self):
        if type(self.job['groups_id']) is list:
            self.groups = self.job['groups_id']
        else:
            self.groups = []
        return

    def cleanup(self):
        """Clean all the model related data"""
        shutil.rmtree(self.data_dir)

    def prepare_dataset(self):
        """Prepare dataset for training"""
        model = self.model

        def downloader(record):
            api.get_image_by_url(record['url'], "", record["path"])

        # TODO: find the right place for the labels file
        label_maker.make(self.labels_file, self.job['classes'])
        if os.path.exists(self.labels_file):
            _LOGGER.info('labels_file exists')
        else:
            _LOGGER.error('labels_file does not exists')

        with TFRConverter(self.data_dir, labels_file=self.labels_file) as tf_converter:
            for group in self.groups:
                _LOGGER.debug("Loading images for group %s" % group)
                page = 1
                bar = None
                while True:
                    res = api.get_last_data({'group_id': group}, extra={'annotated': 1, 'page': page})
                    # res = api.get_last_data({'group_id': group}, extra={'annotated': 1, 'page': page, 'trained': 0})
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
                        page += 1
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

    def check_for_base_model(self, base_checkpoints_path, model):
        ''' check if the base model exists. else download '''
        if not os.path.exists(os.path.join(base_checkpoints_path, 'checkpoint', 'ckpt-0.index')):
            _LOGGER.debug(f"Base model not found for {model['architecture']}, Downloading now.")
            model_filename_tar = api.download_tf2_model_files(model['architecture'])
            if tarfile.is_tarfile(model_filename_tar):
                _LOGGER.debug("Tar file found")
                ensure_path(base_checkpoints_path)
                shutil.unpack_archive(model_filename_tar, config.BASE_MODELS_PATH)
                os.remove(model_filename_tar)
            else:
                _LOGGER.error("Invalid file")
                return False
        return True

    def get_checkpoint(self, job, model, train_dir):
        ''' find the relevant checkpoint '''
        base_checkpoints_path = None

        # TODO: add logic to resume training
        # if not os.path.exists(os.path.join(train_dir, 'checkpoint')):
        if True:
            # there are no checkpoints available in the train directory
            _LOGGER.debug("No checkpoints exists to resume training")

            base_checkpoints_path = os.path.join(config.BASE_MODELS_PATH, model['architecture'])
            _tmf = os.path.join(config.TRAINED_MODELS_DATA, model['file_name'])
            # if os.path.isdir(_tmf):
            #     _LOGGER.debug(f"Model already trained before. Continuing from the saved checkpoint found in {_tmf}")
            #     base_checkpoints_path = _tmf
            # elif model['type'] == 'new':
            if model['type'] == 'new':
                _LOGGER.debug(f"Training new model from a base model {model['architecture']}")
                if not self.check_for_base_model(base_checkpoints_path, model):
                    return False
            else:
                parent_model = api.get_model(model['parent'])
                if not parent_model:
                    raise FileNotFoundError(f"Parent model {model['parent']} not found on server")
                _LOGGER.debug(f"Training new model from the parent model {parent_model['file_name']}")

                parent_tmf = os.path.join(config.TRAINED_MODELS_DATA, parent_model['file_name'])
                if os.path.isdir(parent_tmf):
                    base_checkpoints_path = parent_tmf
                else:
                    _LOGGER.error("Parent model not found. please train it first")
                    return False

            if os.path.exists(train_dir):
                shutil.rmtree(train_dir)
            shutil.copytree(os.path.join(base_checkpoints_path, 'checkpoint'), train_dir)
            if os.path.exists(os.path.join(train_dir, 'checkpoint', 'checkpoint')):
                os.remove(os.path.join(train_dir, 'checkpoint', 'checkpoint'))

        if base_checkpoints_path:
            if glob.glob(os.path.join(base_checkpoints_path, 'checkpoint', 'ckpt-*.index')):
                # _LOGGER.info('A checkpoint already exists. Fine tuning')
                job['checkpoint'] = self.copy_ckpt(train_dir)
                
                # remove all the copied checkpoints
                filenames = glob.glob(os.path.join(train_dir, 'ckpt*'))
                for filename in filenames:
                    os.remove(filename)
                # remove all the checkpoint file
                if os.path.exists(os.path.join(train_dir, 'checkpoint')):
                    os.remove(os.path.join(train_dir, 'checkpoint'))
                return True

        if glob.glob(os.path.join(train_dir, 'ckpt-*.index')):
            # checkpoint already exists in the train directory => resume training
            _LOGGER.info(f'Resuming Training. A checkpoint already exists in {train_dir}')
            job['checkpoint'] = self.copy_ckpt(train_dir)
            if os.path.exists(os.path.join(train_dir, 'checkpoint', 'checkpoint')):
                os.remove(os.path.join(train_dir, 'checkpoint', 'checkpoint'))
            return True
        return False

    def run_command(self, command, logger_filename):
        ''' run training or evaluation and save the output to a file '''
        _LOGGER.debug('executing the command: ')
        [_LOGGER.debug(f'{line}') for line in command]
        try:
            tail = TailThread(self.job, self.job['steps'], logger_filename)
            tail.start()
            with open(logger_filename, 'a') as logger:
                process = subprocess.run(command, check=True, stdout=logger, stderr=logger)
        except Exception as exc:
            _LOGGER.error(f'Error: {str(exc)}')
            self.status = False
            raise
        else:
            self.status = True
        finally:
            tail.stop()
            if tail.is_alive():
                _LOGGER.info('Waiting for tail thread to close')
                tail.join()
                _LOGGER.info('Tail thread closed successfully')
            return self.status

    def _train(self, job, logger_filename):
        ''' run a training '''
        filename = os.path.expanduser('~/tensorflow/models/research/object_detection/model_main_tf2.py')
        command = [
            f"python3",
            filename,
            # f"/tensorflow/models/research/object_detection/model_main_tf2.py",
            f"--model_dir={self.train_dir}",
            # f"--num_train_steps={job['steps']}",
            f"--sample_1_of_n_eval_examples=1",
            f"--pipeline_config_path={self.pipeline_config_path}",
            f"--checkpoint_every_n={self.evalStep}",
            f"--alsologtostderr",
        ]
        try:
            self.run_command(command, logger_filename)
        except Exception as exc:
            _LOGGER.exception(str(exc))
            _LOGGER.error('Training failed')
            api.update_job_state(self.job, 'error', f'train: {str(exc)}')
        finally:
            return self.status

    def _eval(self, job, logger_filename):
        ''' run evaluation on the current training '''
        filename = os.path.expanduser('~/tensorflow/models/research/object_detection/model_main_tf2.py')
        command = [
            f"python3",
            filename,
            # f"/tensorflow/models/research/object_detection/model_main_tf2.py",
            f"--model_dir={self.train_dir}",
            # f"--num_train_steps={job['steps']}",
            f"--sample_1_of_n_eval_examples=1",
            f"--pipeline_config_path={self.pipeline_config_path}",
            f"--checkpoint_every_n={self.evalStep}",
            f"--checkpoint_dir={self.train_dir}",
            f"--eval_timeout=1",
            f"--eval_on_train_data=false",
            # '--wait_interval=1',
            # '--timeout=1',
            "--alsologtostderr",
        ]
        try:
            self.run_command(command, logger_filename)
        except Exception as exc:
            _LOGGER.exception(str(exc))
            _LOGGER.error('Evaluation failed')
            api.update_job_state(self.job, 'error', f'eval: {str(exc)}')
        finally:
            return self.status
        
    def load_stats(self, train_dir):
        counts = {'train': 0, 'test': 1000, 'classes': 1}
        stats_file = os.path.join(train_dir, "data", "stats.json")
        with contextlib.suppress(Exception):
            with open(stats_file, 'r') as handler:
                counts = json.load(handler)
        return counts

    def copy_exported(self, train_dir, trained_dir, model):
        expected_file = os.path.join(trained_dir, 'saved_model', 'saved_model.pb')
        if not os.path.exists(expected_file):
            return False

        # Successfully exported
        export_dir = os.path.join(config.EXPORTED_MODELS, model['file_name'])
        if os.path.exists(export_dir):
            time_str = datetime.now().strftime('%y%m%d_%H%M%S')
            newname = os.path.join(config.EXPORTED_MODELS, f"{model['file_name']}_{time_str}")
            os.rename(export_dir, newname)
        shutil.copytree(trained_dir, export_dir)
        shutil.copy(
            self.labels_file,
            os.path.join(export_dir, f"{model['file_name']}.pbtxt")
        )
        return True

    def start_training(self):
        """Start training for the model"""
        train_dir = self.train_dir
        job = self.job
        num_steps = int(job['steps'])
        job = api.update_job_state(job, 'training', f'Start training for {num_steps} steps')
        model = self.model

        if not self.get_checkpoint(job, self.model, self.train_dir):
            return False

        if os.path.exists(os.path.join(train_dir, 'data')):
            shutil.rmtree(os.path.join(train_dir, 'data'))
        shutil.copytree(self.data_dir, os.path.join(train_dir, 'data'))

        self.labels_file = os.path.join(train_dir, 'data', 'labels.pbtxt')                        # updating the labels file path
        counts = self.load_stats(train_dir)
        # self.get_checkpoint(job)
        if not self.edit_pipeline(job, model, counts):
            _LOGGER.error('edit_pipeline failed')
            return False

        if not self.train_and_eval(job):
            return False

        trained_dir = os.path.join(config.TRAINED_MODELS_DATA, model['file_name'])
        if os.path.exists(trained_dir):
            shutil.rmtree(trained_dir)
        exporter.export(job, model, trained_dir, self.train_dir)

        if self.copy_exported(train_dir, trained_dir, model):
            _LOGGER.info('Finished Training')
            # api.update_job_state(job, 'done', 'Training complete')
            if os.path.exists(train_dir):
                shutil.rmtree(train_dir)
            return True
        return False
