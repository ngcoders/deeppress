import os
from deeppress.config import config
train_dir = '{}/job_{}'.format(config.TRAIN_DIR, '123')
print(train_dir)