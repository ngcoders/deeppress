"""Make class labels"""
from google.protobuf import text_format
from object_detection.protos import string_int_label_map_pb2
# from object_detection.utils import label_map_util

import api


def make(filename):
    """Make labels and save into a file"""
    label_map = string_int_label_map_pb2.StringIntLabelMap()
    all_items = []

    res = api.get_classes()
    if isinstance(res, dict) and 'data' in res.keys():
        data = res['data']
        total = res['total']
        if total == 0:
            all_items.append('person')  # No class then use person only
        for _c in data:
            all_items.append(_c['class'])

    for i in range(len(all_items)):
        item = label_map.item.add()
        item.id = i + 1
        item.name = all_items[i]
        print("{}: {}".format(i+1, all_items[i]))

    f = open(filename, "w")
    f.write(text_format.MessageToString(label_map))
    f.close()

    # label_map = label_map_util.load_labelmap(filename)
    # categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=100, use_display_name=False)
    # category_index = label_map_util.create_category_index(categories)
    # print(category_index)

if __name__ == '__main__':
    make('test.pbtxt')