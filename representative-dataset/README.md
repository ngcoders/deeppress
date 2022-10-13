# DeepPress

Image Classification and Object Detection

Based on Tensorflow, Tensorflow models (Object detection) and Keras.

Using WordPress plugin for annotation and keep track of data.

## Object Detection
The object detection module is based in [Tensorflow Object Detection API](https://github.com/tensorflow/models/tree/master/research/object_detection).
Setup instructions are given [here](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md).
The API is under development so we are supporting it till commit [ee6fdda](https://github.com/tensorflow/models/commit/ee6fdda13b2cb79d96303a8ef06ad50dee325611).
You can simply checkout to this commit.

## Classification



## Setup

Setup WordPress and install plugin.

Now install python package requirements by running `pip3 install -r requirements.txt`

```
python3 -m deeppress --config=<path-to-config-file>
```

Example config file `deeppress.conf.example`, Copy it and make your changes. Update
WordPress host details.
