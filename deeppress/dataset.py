import requests
import json
import os
from PIL import Image, ImageFile
from io import BytesIO
url = "http://192.168.0.12:8000/wp-json/deeppress/v1/classification/"
base_url = "http://192.168.0.12:8000"
headers = {
    'Authorization': "Basic YWRtaW46YWRtaW4=",
    'Cache-Control': "no-cache",
    'Postman-Token': "88394bc2-67ae-4120-b4bb-d2d63b52424c"
    }
ImageFile.LOAD_TRUNCATED_IMAGES = True
def get_data(endpoint):
    response = requests.request("GET", endpoint, headers=headers)
    result = response.json()
    return result


def request_categories():
    result = get_data(url)
    categories_id = []
    categories_name = []
    cat_dict = {}
    for res in result['data']:
        cat_id = int(res['id'])
        cat_name = res['category']
        if cat_id not in categories_id:
           categories_id.append(cat_id)
           categories_name.append(cat_name)
    for i in range(0,len(categories_id)):
        cat_dict[categories_id[i]] = categories_name[i]

    return cat_dict, categories_id    

def prepare_dataset(categories_id):
    for category in categories_id:
        cat_url = url + "{}/images".format(category)
        result = get_data(cat_url)
        for res in result['data']:
            im_url = base_url + res
            response = requests.get(im_url)
            img = Image.open(BytesIO(response.content))
            os.mkdir('/home/aditya/datasets/
            img.save('/home/aditya/dataset/{}.jpg'.format(res[-15:-4]))
        print("category {} images saved".format(category))
    print("complete dataset saved")

