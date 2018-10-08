import requests
import json
import os
from PIL import Image, ImageFile
from io import BytesIO
import logging
from deeppress.config import config
url = os.path.join(config.WP_MODULES_URL, "/classification")
base_url = config.WP_BASE_URL
headers = {
    'Authorization': "Basic YWRtaW46YWRtaW4=",
    'Cache-Control': "no-cache",
    'Postman-Token': "88394bc2-67ae-4120-b4bb-d2d63b52424c"
    }
ImageFile.LOAD_TRUNCATED_IMAGES = True
_logger = logging.getLogger('backend.dataset')


def get_data(endpoint):
    response = requests.request("GET", endpoint, headers=headers)
    result = response.json()
    return result


def request_categories(categories):
    """This function arranges the categories taken as argument (in the raw form)
    in the form a dictionary with category ID as is keys so that dataset could 
    be prepared
    """

    _logger.debug("getting categories")
    result = get_data(url)
    categories_id = []
    categories_name = []
    cat_dict = {}
    for res in result['data']:
        cat_id = int(res['id'])
        cat_name = res['category']
        if cat_name in categories:
            if cat_name not in categories_name:
                categories_id.append(cat_id)
                categories_name.append(cat_name)
            else:
                continue
    for i in range(0,len(categories_id)):
        cat_dict[categories_id[i]] = categories_name[i]

    return cat_dict, categories_id    
    

def prepare_dataset(categories_id, filename):
    """This function prepares the dataset for all the categories and saves it in
    a local directory (/<filename>/dataset/) and returns the path of the dataset 
    saved
    """
    
    _logger.debug("preparing dataset on machine")
    path = os.path.join(config.DATASET_DIR, filename)
    os.makedirs(path, exist_ok = True)
    img_count=0
    for category in categories_id:
        cat_url = url + "{}/images".format(category)
        result = get_data(cat_url)
        cat_path = path + '{}/'.format(category)
        os.makedirs(cat_path, exist_ok = True)
        for res in result['data']:
            img_count += 1
            im_url = base_url + res
            response = requests.get(im_url)
            img = Image.open(BytesIO(response.content))
            img.save(cat_path + ('/{}.jpg'.format(res[-15:-4])))
        if img_count > config.MINIMUM_TRAIN_DATASET:
            print("category {} images saved".format(category))
        else:
            raise Exception("Images uploaded not enough for classification")
    print("complete dataset saved")
    return os.path.abspath(path)


#cat_dict, categories_id = request_categories()
#path = prepare_dataset(categories_id, "wtpsth")
#print(path, cat_dict)
