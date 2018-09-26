import tensorflow as tf
from google.protobuf import text_format
from object_detection import exporter
from object_detection.protos import pipeline_pb2


def export(pipeline_config_path, output_directory, trained_checkpoint_prefix):
    input_type = 'image_tensor'
    write_inference_graph = False
    pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()

    with tf.gfile.GFile(pipeline_config_path, 'r') as f:
        text_format.Merge(f.read(), pipeline_config)

    input_shape = None
    exporter.export_inference_graph(input_type, pipeline_config,
                                    trained_checkpoint_prefix,
                                    output_directory, input_shape,
                                    write_inference_graph)


if __name__ == '__main__':
    export('models/pipeline.config', 'out_put', 'models')