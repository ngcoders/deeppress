"""Make class labels"""
from google.protobuf import text_format
from object_detection.protos import string_int_label_map_pb2


def make(filename, classes):
    """Make labels and save into a file"""
    label_map = string_int_label_map_pb2.StringIntLabelMap()

    for i, label_name in enumerate(classes):
        item = label_map.item.add()
        item.id = i + 1
        item.name = label_name
        print(f'{i + 1}: {label_name}')

    with open(filename, 'w') as handle:
        handle.write(text_format.MessageToString(label_map))

if __name__ == '__main__':
    make('test.pbtxt', ['person', 'computer'])