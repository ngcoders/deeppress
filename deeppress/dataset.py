import requests
import json
import os
from PIL import Image, ImageFile
from io import BytesIO
import logging
from deeppress import api
from deeppress.config import config


ImageFile.LOAD_TRUNCATED_IMAGES = True
_logger = logging.getLogger('backend.dataset')


def get_data(endpoint):
    response = requests.request("GET", endpoint, auth=(config.WP_USERNAME, config.WP_PASSWORD), timeout=10)
    result = response.json()
    if isinstance(result['data'], dict) and 'id' not in result['data'].keys():
        _logger.error("Invalid data")
        result = False
    return result


def request_categories(categories):
    """This function arranges the categories taken as argument (in the raw form)
    in the form a dictionary with category ID as is keys so that dataset could 
    be prepared
    """
    url = config.WP_MODULES_URL + "/classification"
    _logger.debug("getting categories")
    result = get_data(url)
    categories_id = []
    categories_name_local = []
    categories_name_global = []
    cat_dict = {}
    if result:
        for res in result['data']:
            cat_id = int(res['id'])
            cat_name = res['category']
            if cat_name in categories:
                categories_id.append(cat_id)
                categories_name_local.append(cat_name)
                if cat_name not in categories_name_global:
                    categories_name_global.append(cat_name)
            else:
                continue
        if len(categories_name_global) < 2:
            _logger.error("categories less than 2")
            return False, False, False
        elif categories_id == []:
            _logger.error("Categories not found")
            return False, False, False       
        else:
            for i in range(0,len(categories_id)):
                cat_dict[categories_id[i]] = categories_name_local[i]
            return cat_dict, categories_id, categories_name_global 
    else:
        return False, False, False
    

def prepare_dataset(categories_id, filename, job, cat_dict):
    """This function prepares the dataset for all the categories and saves it in
    a local directory (/<filename>/dataset/) and returns the path of the dataset 
    saved
    """
    
    _logger.debug("preparing dataset on machine")
    path = os.path.join(config.DATASET_DIR, filename)
    base_url = config.WP_BASE_URL
    url = config.WP_MODULES_URL + "/classification"
    os.makedirs(path, exist_ok = True)
    img_count=0
    cat_count=len(cat_dict.keys())
    for category in categories_id:
        cat_url = url + "/{}/images".format(category)
        result = get_data(cat_url)
        if result:
            
            cat_path = path + '/{}'.format(cat_dict[category])
            os.makedirs(cat_path, exist_ok = True)
            for res in result['data']:
                img_count += 1
                im_url = base_url + res
                response = requests.get(im_url)
                try:
                    img = Image.open(BytesIO(response.content))
                    img.save(cat_path + ('/{}.jpg'.format(res[-15:-4])))
                except OSError:
                    _logger.error("failed to download the image")
                    img_count -= 1
                    continue
            status = api.update_job_state(job, 'running', 'Preparing dataset complete')
        else:
            _logger.error("Could not obtain data for {} category".format(category))
            continue
    
    if img_count < config.MINIMUM_TRAIN_DATASET or (cat_count < 2):
        status = api.update_job_state(job, 'error', 'Dataset not enough for training')
        _logger.error("dataset small")
        return False, []
    else:
        return True, os.path.abspath(path)


#cat_dict, categories_id = request_categories()
#path = prepare_dataset(categories_id, "wtpsth")
#print(path, cat_dict)
