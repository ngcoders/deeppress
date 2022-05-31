import logging
import subprocess


_LOGGER = logging.getLogger('deeppress.exporter')

def export(pipeline_config_path, output_directory, trained_checkpoint_dir):
    '''
        python3 /tensorflow/models/research/object_detection/exporter_main_v2.py \
        --input_type=image_tensor \
        --pipeline_config_path=data/trained_models/0_1000_test2_efficientdet_d3_211103_115143/pipeline.config \
        --trained_checkpoint_dir=data/trained_models/0_1000_test2_efficientdet_d3_211103_115143/ \
        --output_directory=data/tflite_models/0_1000_test2_efficientdet_d3_211103_115143
    '''
    command = [
        'python3',
        '/tensorflow/models/research/object_detection/exporter_main_v2.py',
        '--input_type=image_tensor',
        f'--pipeline_config_path={pipeline_config_path}',
        f'--trained_checkpoint_dir={trained_checkpoint_dir}',
        f'--output_directory={output_directory}',
    ]
    _LOGGER.debug('executing the command: ')
    [_LOGGER.debug(f'{line}') for line in command]
    result = subprocess.run(command, stdout=subprocess.PIPE)
    _LOGGER.info(str(result.stdout, 'UTF-8'))


if __name__ == '__main__':
    export('models/pipeline.config', 'out_put', 'models')