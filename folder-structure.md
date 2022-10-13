# FOLDER STRUCTURE FOR DEEPPRESS

This is a document detailing the folder structure and naming conventions followed in Avuity Software projects, especially for Deeppress.

## Avuity Software Folder Layout

The Avuity Software folder layout is as follows

    .
    ├── src                         # all the source code resides here
    |   ├── deeppress               # source code for deeppress
    |   ├── gateway                 # source code for gateway
    |   ├── pal                     # source code for central detector
    |   ├── sensors                 # source code for all types of sensors
    |   ├── vusensor                # 
    |   └── README.md               # Readme file
    ├── ActiveProjects.txt          # list of active projects
    └── README.md                   # readme file

## Deeppress Folder Overview

The `deeppress` project is located in `avuity_software/src/deeppress`. The structure of the deeppress project is as follows

    .
    └── deeppress                   # all the source code resides here
        ├── python                  # source code for the tensorflow back end
        ├── wordpress               # source code for the wordpress front end
        └── docs                    # documentation including API docs

## Tensorflow Backend Folder Layout

The source code for the tensorflow back end is located in `avuity_software/src/deeppress/python`. The files and folders denoted by `(C)` is used to implement Classification and the ones denoted by `(OD)` are used to implement Object Detection functionalities exclusively. The rest of the files are common for both functionalities. It is to be noted that at the time of writing, the classification functionality of Tensorflow 1 has not been ported to Tensorflow 2. 

The structure of the python folder is as follows

    ├── data                            # we will see this is detail
    |   └── files
    ├── deeppress
    |   ├── configs                     # contains the config files used by tensorflow 1
    |   |   └── config files
    |   ├── detection
    |   |   └── __init__.py             # the source code for tensorflow 1 detection (OD)
    |   ├── tf2_detection
    |   |   └── __init__.py             # the source code for tensorflow 2 detection (OD)
    |   ├── job.py                      # object detection training jobs (OD)
    |   ├── model_files_info.py         # tensorflow 1 and 2 model file information (OD)
    |   ├── exporter.py                 # export the trained files into other formats (OD)
    |   ├── api.py                      # all api interactions with the outside world
    |   ├── app.py                      # deeppress app
    |   ├── app_exceptions.py           # handles app exceptions
    |   ├── utils.py                    # mixed utilities
    |   ├── trainer.py                  # trainer class (C)
    |   ├── train.py                    # train class (C)
    |   ├── predict.py                  # predict functionalities (C)
    |   ├── models.py                   # model details (C)
    |   ├── dataset.py                  # prepare dataset (C)
    |   ├── classifier_backend_main.py  # classification job (C)
    |   ├── label_maker.py              # make labels
    |   ├── image_to_tfr.py             # convert image to tfrecord
    |   ├── eval.py                     # run evaluation (OD) - not used in TF2
    |   ├── config.py                   # extract and set configurations
    |   ├── bottle.py                   # source code for bottle
    |   ├── __main__.py                 # main file
    |   ├── __init__.py                 # init file
    |   └── web.py                      # web functionalities
    ├── README.md                       # readme file
    ├── deeppress.conf                  # configuration file
    ├── deeppress.conf.example          # example configuration file
    ├── setup.py
    ├── requirements.txt                # pip requirements for deeppress
    ├── Classification Models.txt       # list of classification models (C)
    └── .gitignore                      # gitignore file

In `avuity_software/src/deeppress/python`, we have a folder named `data`. The folder name `data` is user configurable and is defined by the value set by `DATA_DIR` found in `avuity_software/src/deeppress/python/deeppress/deeppress.conf`.

```
# Path where trained models and data will be stored
DATA_DIR = "data"
```

### Data Folder Layout

In case of changing the name of this folder, one can change the value in `deeppress.conf` and re-run the application.

Names of each of the folders present inside `data` folder are associated with training and exporting models. These are defined in `config.py`. The values are

| Variable                |  | Path                    |
|------------------------:|--|:------------------------|
| BASE_MODELS_PATH        |  | data/base_models        |
| DATASET_DIR             |  | data/dataset            |
| DOWNLOADS_DIR           |  | data/downloads          |
| EVAL_DIR                |  | data/eval_dir           |
| TRAIN_DIR               |  | data/train              |
| TRAINED_MODELS_DATA     |  | data/trained_models     |
| EXPORTED_MODELS         |  | data/exported_models    |
| TFLITE_MODELS           |  | data/tflite_models      |
| LOG_DIR                 |  | data/logs               |

In case of changing the names of these folders, one can change the values in `config.py` and re-run the application.

Let us take a look at the `data` folder

    └── data
        ├── base_models                 # contains the base model downloaded from the tensorflow 2 model zoo
        |   ├── model1                  # each folder has the extracted model with supporting files such as pipeline.config
        |   ├── model2
        |   └── model3
        ├── dataset                     # contains the data needed for training (tfrecord, labels file and stats)
        |   ├── job1                    # each folder has dataset associated with each job
        |   ├── job2
        |   └── job3
        ├── downloads                   # unused
        ├── eval_dir                    # unused
        ├── train                       # contains the files generated by tensorflow during training (deleted after a successful training)
        |   ├── job_1                   # (if present) each folder has the training files generated by tensorflow associated with each job
        |   ├── job_2
        |   └── job_3
        ├── trained_models              # contains the last checkpoint and saved model of each training
        |   ├── job_filename_1          # the foldername is defined by the entry `file name` defined in `models` (front end)
        |   ├── job_filename_2
        |   └── job_filename_3
        ├── exported_models             # exported file (checkpoint and saved model) of each training
        |   ├── job_filename_1          # the foldername is defined by the entry `file name` defined in `models` (front end)
        |   ├── job_filename_2
        |   └── job_filename_3
        ├── tflite_models               # checkpoint of each training converted to tflite and edgetpu
        |   ├── job_filename_1          # the foldername is defined by the entry `file name` defined in `models` (front end)
        |   ├── job_filename_2
        |   └── job_filename_3
        └── logs                        # contains the logs of each and every training and evaluation

### Folder Layout Of Files Generated By Tensorflow

All the folders inside `train` has the following structure

    └── job_<number>
        ├── data
        |   ├── labels.pbtxt            # labels file
        |   ├── stats.json              # stats describing the number of classes and images for training and evaluation 
        |   |                           # (eg: {"train": 18927, "test": 4736, "classes": 1})
        |   |                           # the rest are tfrecords for training and evaluation
        |   ├── test_baheads.tfrecord-220801_132442
        |   └── train_baheads.tfrecord-220801_132442
        ├── checkpoint_dir              # custom folder created to run evaluation on the latest checkpoint
        |   |                           # this is a workaround to run training and evaluation simultaneously
        |   ├── checkpoint              # file pointing to the latest checkpoint
        |   ├── ckpt-3.index            # the latest checkpoint files copied for evaluation
        |   └── ckpt-3.data-00000-of-00001
        ├── train                       # train events generated by tensorflow during training
        |   ├── events.out.tfevents.1659365352.devpal.191577.0.v2
        |   └── events.out.tfevents.1659361291.devpal.191197.0.v2
        ├── eval                        # eval events generated by tensorflow during evaluation
        |   └── events.out.tfevents.1659363968.devpal.191440.0.v2
        ├── pipeline.config             # pipeline config paths
        ├── checkpoint                  # file pointing to the latest checkpoint
        ├── ckpt-3.index                # the rest are the checkpoint files generated during training
        ├── ckpt-3.data-00000-of-00001
        ├── ckpt-2.index
        ├── ckpt-2.data-00000-of-00001
        ├── ckpt-1.index
        └── ckpt-1.data-00000-of-00001

### Folder Layout Of Trained And Exported Tensorflow Models

All the folders inside `trained_models` and `exported_models` has the following structure

    └── <foldername>
        ├── <foldername>.pbtxt          # (if present) contains the labels file for the particular job
        ├── pipeline.config             # file contains the pipeline configurations used for the training
        ├── checkpoint                  # folder contains the checkpoint files associated with the training
        |   ├── checkpoint
        |   ├── ckpt-0.index
        |   └── ckpt-0.data-00000-of-00001
        └── saved_model                 # contains the saved model files associated with the training
            ├── saved_model.pb          # the serialized description of the computation along with parameter values defined by the model
            ├── assets                  # usually empty
            └── variables
                ├── variables.index
                └── variables.data-00000-of-00001

This sums up most of the file structures found inside deeppress project.

> **ℹ️ <font color="blue">INFO </font>** \
> AUTHOR: ALLAN TOM MATHEW\
> DATE: 06-10-2022\
> VERSION: v1.0
