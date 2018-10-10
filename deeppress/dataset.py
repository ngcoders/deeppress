import requests
import json
import os
from PIL import Image, ImageFile
from io import BytesIO
import logging
import api
from deeppress.config import config
url = os.path.join(config.WP_MODULES_URL, "/classification")
base_url = config.WP_BASE_URL
ImageFile.LOAD_TRUNCATED_IMAGES = True
_logger = logging.getLogger('backend.dataset')


def get_data(endpoint):
    response = requests.request("GET", endpoint, auth=(config.WP_USERNAME, config.WP_PASSWORD), timeout=10)
    result = response.json()
    if isinstance(result['data'], dict) and 'id' not in result['data'].keys():
        _logger.error("Invalid data")
        result = False
        print("Error : Invalid data recieved")
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
    if result:
        for res in result['data']:
            cat_id = int(res['id'])
            cat_name = res['category']
            if cat_name in categories:
                if cat_name not in categories_name:
                    categories_id.append(cat_id)
                    categories_name.append(cat_name)
                else:
                    continue
        if len(categories_id) < 2:
            _logger.error("categories less than 2")
            print("Error : Need more categories than 2")
            return False, False
        elif categories_id == []:
            _logger.error("Categories not found")
            print("Error : Categories not found, Try again")
            return False, False       
        else:
            for i in range(0,len(categories_id)):
                cat_dict[categories_id[i]] = categories_name[i]
            return cat_dict, categories_id 
    else:
        return False, False
    

def prepare_dataset(categories_id, filename, job):
    """This function prepares the dataset for all the categories and saves it in
    a local directory (/<filename>/dataset/) and returns the path of the dataset 
    saved
    """
    
    _logger.debug("preparing dataset on machine")
    path = os.path.join(config.DATASET_DIR, filename)
    os.makedirs(path, exist_ok = True)
    img_count=0
    cat_count=0
    for category in categories_id:
        cat_url = url + "{}/images".format(category)
        result = get_data(cat_url)
        if result:
            cat_count += 1
            cat_path = path + '{}/'.format(category)
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
                    print("inavlid image")
                    img_count -= 1
                    continue
            status = api.update_job_state(job, 'running', 'Preparing dataset complete')
        else:
            _logger.error("Could not obtain data for {} category".format(category))
            print("Error : Could not obtain data for {} category".format(category) )
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
