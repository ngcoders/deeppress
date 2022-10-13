import os
import re
import cv2
import logging
import subprocess
import subprocess
import numpy as np
from glob import glob


_LOGGER = logging.getLogger('deeppress.exporter')


def export_ckpt(pipeline_config_path, output_directory, trained_checkpoint_dir):
    '''
        export a checkpoint file
        python3 /tensorflow/models/research/object_detection/exporter_main_v2.py \
        --input_type=image_tensor \
        --pipeline_config_path=data/trained_models/0_1000_test2_efficientdet_d3_211103_115143/pipeline.config \
        --trained_checkpoint_dir=data/trained_models/0_1000_test2_efficientdet_d3_211103_115143/ \
        --output_directory=data/tflite_models/0_1000_test2_efficientdet_d3_211103_115143
    '''
    filename = os.path.expanduser('~/tensorflow/models/research/object_detection/exporter_main_v2.py')
    command = [
        'python3',
        filename,
        # '/home/pal/tensorflow/models/research/object_detection/exporter_main_v2.py',
        '--input_type=image_tensor',
        f'--pipeline_config_path={pipeline_config_path}',
        f'--trained_checkpoint_dir={trained_checkpoint_dir}',
        f'--output_directory={output_directory}',
    ]
    _LOGGER.debug('executing the command: ')
    [_LOGGER.debug(f'{line}') for line in command]
    result = subprocess.run(command, stdout=subprocess.PIPE)
    _LOGGER.info(str(result.stdout, 'UTF-8'))


class TF2LiteConverter():
    def __init__(self, job, trained_checkpoint_dir, architecture):
        ''' initialize the variables '''
        if not os.path.exists(job['tfliteDir']):
            os.makedirs(job['tfliteDir'])
        self.trained_checkpoint_dir = trained_checkpoint_dir
        job['exportedGraphDir'] = job['tfliteDir']
        # job['exportedGraphDir'] = os.path.join(job['tfliteDir'], 'exported_graph')
        job['exportedGraphFile'] = os.path.join(job['exportedGraphDir'], 'saved_model', 'saved_model.pb')
        # job['exportedGraphFile'] = os.path.join(job['tfliteDir'], 'tflite_graph.pb')
        job['tfliteFile'] = os.path.join(job['tfliteDir'], 'output_tflite_graph.tflite')
        job['edgetpuTfliteFile'] = os.path.join(job['tfliteDir'], 'output_tflite_graph_edgetpu.tflite')
        self.job = job
        # to calculate the resolution
        searchStr = r'_(?P<res1>\d+)x(?P<res2>\d+)_'
        if search := re.search(searchStr, architecture):
            self.image_resolution = (search['res1'], search['res2'])
        else:
            self.image_resolution = None
        _LOGGER.debug(f'Model input resolution: {self.image_resolution[0]} x {self.image_resolution[1]}')

    def export_graph(self):
        '''
            export the ssd checkpoint to tflite ssd graph
            example usage:
            python scripts/export_tflite_ssd_graph.py \
            --pipeline_config_path="data/trained_models/bababa101010_ssd_inception_v2_210224_110000/pipeline.config" \
            --trained_checkpoint_prefix="data/trained_models/bababa101010_ssd_inception_v2_210224_110000/model.ckpt-270000" \
            --output_directory="manual_conversion/tflite3" \
            --add_postprocessing_op=true
        '''
        _LOGGER.info('Initiating export of the checkpoint to tflite ssd graph')
        _LOGGER.debug('job[\'pipeline_config_path\']: {}'.format(self.job['pipeline_config_path']))
        filename = os.path.expanduser('~tensorflow/models/research/object_detection/export_tflite_graph_tf2.py')
        command = [
            'python3',
            filename,
            # '/home/pal/tensorflow/models/research/object_detection/export_tflite_graph_tf2.py',
            f'--pipeline_config_path={self.job["pipeline_config_path"]}',
            f'--trained_checkpoint_dir={self.trained_checkpoint_dir}',
            f'--output_directory={self.job["exportedGraphDir"]}',
            '--max_detections=20',
            '--ssd_use_regular_nms=true',
            # '--add_postprocessing_op=true',
        ]
        _LOGGER.debug('executing the command: ')
        # [_LOGGER.debug(f'{line}') for line in command]
        _LOGGER.debug('\n'.join(command))
        result = subprocess.run(command, stdout=subprocess.PIPE)
        _LOGGER.info(str(result.stdout, 'UTF-8'))
        return bool((os.path.exists(self.job['exportedGraphFile'])))

    def representative_dataset_gen(self):
        ''' generate representative dataset. This acts as sample dataset for tflite conversion '''
        for filename in glob('representative-dataset/*.jp*g'):
            # file_path = os.path.normpath(os.path.join(image_path, filename))
            img = cv2.imread(filename)
            # img = cv2.resize(img, (640, 640))
            img = cv2.resize(img, self.image_resolution)
            img = img / 255.0
            # img = np.reshape(img, (1, 640, 640, 3))
            img = np.reshape(img, (1, *self.image_resolution, 3))
            image = img.astype(np.float32)
            yield [image]

    def convert_to_tflite(self):
        ''' convert the exported graph to tflite '''
        _LOGGER.info('Initiating conversion of the exported graph to tflite')

        import tensorflow as tf
        converter = tf.lite.TFLiteConverter.from_saved_model(os.path.dirname(self.job['exportedGraphFile']))
        converter.representative_dataset = self.representative_dataset_gen
        # converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8, tf.lite.OpsSet.TFLITE_BUILTINS]
        # converter.target_spec.supported_ops = [tf.lite.OpsSet.SELECT_TF_OPS]
        # converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_model = converter.convert()
        with open(self.job['tfliteFile'], 'wb') as handle:
            handle.write(tflite_model)

        return bool((os.path.exists(self.job['tfliteFile'])))

    def edgetpu_compile(self):
        _LOGGER.info('Initiating compilation of tflite file for edgetpu')
        command = [
            'edgetpu_compiler',
            '-o',
            self.job['tfliteDir'],
            self.job['tfliteFile'],
        ]
        _LOGGER.debug('executing the command: ')
        _LOGGER.debug('\n'.join(command))
        result = subprocess.run(command, stdout=subprocess.PIPE)
        _LOGGER.info(str(result.stdout, 'UTF-8'))
        return bool((os.path.exists(self.job['edgetpuTfliteFile'])))

    def convert(self):
        ''' convert an ssd model into a tensorflow 2 lite model '''
        try:
            if(self.export_graph()):
                _LOGGER.info('\n*** Converted checkpoint to frozen graph ***\n')

                if(self.convert_to_tflite()):
                    _LOGGER.info('\n*** Converted frozen graph to tflite ***\n')

                    if(self.edgetpu_compile()):
                        _LOGGER.info('\n*** Compiled for edgetpu ***\n')
                        return True
                    else:
                        _LOGGER.error('\n*** Error: Compilation for edgetpu failed ***\n')
                        # api.update_gateway_data_with_status(job, 'Compilation of tflite file for edgetpu failed')

                else:
                    _LOGGER.error('\n*** Error: Convertion of frozen graph to tflite Failed ***\n')
            else:
                _LOGGER.error('\n*** Error: Exporting Frozen Graph Failed ***\n')
        except Exception as exc:
            _LOGGER.exception(str(exc))
        return False


def export(job, model, output_directory, trained_checkpoint_dir):
    export_ckpt(job['pipeline_config_path'], output_directory, trained_checkpoint_dir)

    if 'ssd_mobilenet' not in model['architecture']:
        return
    try:
        converter = TF2LiteConverter(job, trained_checkpoint_dir, model['architecture'])
        converter.convert()
    except Exception as exc:
        print(f'Error {str(exc)}')


if __name__ == '__main__':
    import sys
    from logging.handlers import RotatingFileHandler
    LOG_LEVEL = logging.DEBUG
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(LOG_LEVEL)
    log_file = '/tmp/deeppress.log'
    fh = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=3)
    fh.setLevel(LOG_LEVEL)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(fmt='%(levelname).1s %(asctime)s.%(msecs).03d: %(message)s [%(pathname)s:%(lineno)d]', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    LOGGER = logging.getLogger('deeppress')
    LOGGER.setLevel(LOG_LEVEL)
    LOGGER.addHandler(ch)
    LOGGER.addHandler(fh)
    LOGGER.propagate = False
    tfl = logging.getLogger('tensorflow')
    tfl.setLevel(logging.INFO)
    # formatter = logging.Formatter(fmt='%(levelname).1s %(asctime)s.%(msecs).03d: %(message)s [%(pathname)s:%(lineno)d]', datefmt='%Y-%m-%d %H:%M:%S')
    # for h in tfl.handlers:
    #     h.setFormatter(formatter)
    _LOGGER = logging.getLogger('deeppress.exporter')
    tfl.addHandler(_LOGGER)
    tfl.propagate = False

    job = {
        # 'pipeline_config_path': '/home/pal/deeppressv2/data/base_models/ssd_mobilenet_v2_fpnlite_640x640_coco17_tpu-8/pipeline.config',
        # 'trained_checkpoint_file': '/home/pal/deeppressv2/data/base_models/ssd_mobilenet_v2_fpnlite_640x640_coco17_tpu-8/checkpoint',
        # 'tfliteDir': '/home/pal/deeppressv2/data/tflite_models/ssd_mobilenet_v2_fpnlite_640x640_coco17_tpu-8',
        'pipeline_config_path': '/home/pal/deeppressv2/data/exported_models/SSDMobilenetv1.2/pipeline.config',
        'trained_checkpoint_file': '/home/pal/deeppressv2/data/exported_models/SSDMobilenetv1.2/checkpoint',
        'tfliteDir': '/home/pal/deeppressv2/data/tflite_models/SSDMobilenetv1.2',
    }
    export(job, True)
