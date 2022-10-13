<style>
body {
    counter-reset: h1
}
h1 {
    counter-reset: h2
}
h2 {
    counter-reset: h3
}
h3 {
    counter-reset: h4
}
h1:before {
    counter-increment: h1;
    /* content: counter(h1) ". "; */
    content: '';
}
h2:before {
    counter-increment: h2;
    content: counter(h2) ". "
}
h3:before {
    counter-increment: h3;
    content: counter(h2) "." counter(h3) ". "
}
h4:before {
    counter-increment: h4;
    content: counter(h2) "." counter(h3) "." counter(h4) ". "
}
</style>

# DEEP PRESS v2

This is a documentation detailing the instructions to set up Deep Press v2

## Pre-Conditions

Make sure the Ubuntu version is 20.04
```
lsb_release -a
```

Make sure the python version is 3.8.*
```
python3 --version
```

Check if NVIDIA graphics card is installed on your machine
```
lspci | grep -i nvidia
```

### A few notable changes in Deep Press v2 are:
1. This runs on tensorflow 2 (tested with 2.9.1)
1. The structure of the model file directory is changed

### Old Structure:
```
   .
   └── models                            # folder which contains the models
       ├── model1.pb                     # name of the model
       └── ssd.pb                        # name of the model; example, ssd
```
### New Structure:
```
   .
   ├── models                            # folder which contains the models
   │   ├── model1                        # name of the model
   │   │   ├── model1.pbtxt              # specific .pbtxt file for this model (optional) (priority over baheads_map.pbtxt)
   │   │   └── saved_model
   │   │       ├── saved_model.pb        # actual model file
   │   │       ├── assets                # usually an empty folder
   │   │       └── variables             # contains variables for the model
   │   │           ├── variables.data-00000-of-00001
   │   │           └── variables.index
   │   └── ssd                           # name of the model; example, ssd
   │       ├── ssd.pbtxt                 # specific .pbtxt file for this model (optional) (priority over baheads_map.pbtxt)
   │       └── saved_model
   │           ├── saved_model.pb        # actual model file
   │           ├── assets                # usually an empty folder
   │           └── variables             # contains variables for the model
   │               ├── variables.data-00000-of-00001
   │               └── variables.index
   └── baheads_map.pbtxt                 # global (default) .pbtxt file
```

A detailed view on the folder structure is described in [Folder Structure](folder-structure.md)

## Removing Previous Installations

To remove CUDA Toolkit:
```
sudo apt --purge remove -y "*cublas*" "cuda*"
```

To remove libcudnn drivers:
```
sudo apt --purge remove -y "libcudnn7*" "libcudnn8*"
```

To remove NVIDIA drivers:
```
sudo apt --purge remove -y "*nvidia*"
sudo apt --purge remove -y "nvidia-driver-*"
```

To remove cuda leftovers
```
sudo rm -rf /usr/local/cuda*
```

To autoremove and autoclean ubuntu packages
```
sudo apt -y update
sudo apt -y autoremove
sudo apt -y autoclean
```

## Install Video Driver

Check nvidia-driver version
```
modinfo nvidia | grep version
```

If installed, remove it
```
sudo apt --purge remove "nvidia-driver-*"
```

Let’s install nvidia-driver-470
```
sudo apt install -y nvidia-driver-470
```

Always ensure you have selected the NVIDIA driver before rebooting.
```
prime-select query
sudo prime-select nvidia
sudo reboot
```

## Install CUDA Toolkit

Commands to install CUDA v11.2 Toolkit if the required files are to be downloaded are:
```
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.2.2/local_installers/cuda-repo-ubuntu2004-11-2-local_11.2.2-460.32.03-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-2-local_11.2.2-460.32.03-1_amd64.deb
sudo apt-key add /var/cuda-repo-ubuntu2004-11-2-local/7fa2af80.pub
sudo apt update
sudo apt -y install cuda-toolkit-11-2
```

## Install cuDNN Library

Check if cuDNN is already installed
```
apt list --installed | grep -i libcudnn
```

If installed, remove it
```
sudo apt --purge remove “libcudnn*”
```

Downloading cuDNN libraries requires a browser, making an account in the Nvidia website and logging in. In a command line, this will be a limitation. It is better to have the files downloaded and ready (see Tips to download the files). Though the files have Cuda v11.3 on the filename, it is meant for Cuda v11.x. The files are:

[libcudnn8_8.2.1.32-1+cuda11.3_amd64.deb](https://developer.nvidia.com/compute/machine-learning/cudnn/secure/8.2.1.32/11.3_06072021/Ubuntu20_04-x64/libcudnn8_8.2.1.32-1+cuda11.3_amd64.deb)

[libcudnn8-dev_8.2.1.32-1+cuda11.3_amd64.deb](https://developer.nvidia.com/compute/machine-learning/cudnn/secure/8.2.1.32/11.3_06072021/Ubuntu20_04-x64/libcudnn8-dev_8.2.1.32-1+cuda11.3_amd64.deb)


> **ℹ️ <font color="blue">Tips to download the files: </font>** 
>
> * This is to be performed in a computer with a browser and a monitor.
> * Copy one of the links and paste it in the browser.
> * When prompted, log in with the Nvidia account or register to get a new account.
> * As soon as we are logged in, the file download will be initiated.
> * From the downloading file, right click and copy the download link. Since we no longer need the file in this machine, we can cancel the download.
> * Go to the headless system where we need the file and open a command prompt, if not opened.
> * Download the file using:
> 
>   `wget -O libcudnn8_8.2.1.32-1+cuda11.3_amd64.deb <link_that_we_copied>`

> * Likewise, copy the second link found above and paste it in the browser
> * Since we have already logged in, the file will be downloaded automatically.
> * From the downloading file, right click and copy the download link. Since we no longer need the file in this machine, we can cancel the download.
> * Go to the headless system where we need the file and open a command prompt, if not opened.
> * Download the file using:
> 
>   `wget -O libcudnn8-dev_8.2.1.32-1+cuda11.3_amd64.deb <link_that_we_copied>`

Commands to install the files are:
```
sudo dpkg -i libcudnn8_8.2.1.32-1+cuda11.3_amd64.deb
sudo dpkg -i libcudnn8-dev_8.2.1.32-1+cuda11.3_amd64.deb
```

To hold the version:
```
sudo apt-mark hold libcudnn8 libcudnn8-dev
```

Check if the hold is applied
```
apt-mark showhold
```

## Update Environment Variables
Almost there! We’ll have to update a couple of environment variables. First, check if CUDA is already in your system path:
```
echo $PATH
echo $LD_LIBRARY_PATH
```

If not, to update, open the `.bashrc` file:
```
nano ~/.bashrc
```

In case the system is run as a `root` user,
```
sudo nano /etc/bash.bashrc
```

Jump to the end of the file and append the following three lines.
```
# NVIDIA CUDA Toolkit
export PATH=/usr/local/cuda-11.2/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-11.2/lib64:$LD_LIBRARY_PATH
```
Reboot the system to put these into effect.

It is possible to execute the modifications without a reboot by running the below commands. If this doesn’t work, please reboot the system.
```
source ~/.bashrc
. ~/.bashrc
```

After reboot, check if the paths are appended:
```
echo $PATH
echo $LD_LIBRARY_PATH
```

## Installing dependencies

To install dependencies
```
sudo apt update -y && \
sudo apt install -y --no-install-recommends \
apt-utils git gpg-agent protobuf-compiler \
python3-cairocffi python3-pil python3-lxml python3-tk \
wget libgl1-mesa-dev \
ffmpeg libsm6 libxext6 \
apt-transport-https ca-certificates gnupg \
&& sudo apt -y autoclean \
&& sudo rm -r /var/lib/apt/lists/*
```
## Install Object Detection

Clone the tensorflow model directory
```
git clone https://github.com/tensorflow/models.git ~/tensorflow/models/
```

Install Object Detection
```
cd ~/tensorflow/models/research/ && protoc object_detection/protos/*.proto --python_out=.
cp object_detection/packages/tf2/setup.py ./
python3 -m pip install .
```

Test the installation.
```
python3 object_detection/builders/model_builder_tf2_test.py
```

## Install Tensorflow GPU

First, uninstall tensorflow-gpu since they are now covered under the same package: (may need to sudo)
```
python3 -m pip uninstall tensorflow-gpu
```

Let’s install and upgrade pip
```
sudo apt install python3-pip
python3 -m pip install --upgrade pip
```

Let’s install TensorFlow GPU.
```
python3 -m pip install tensorflow==2.9.*
```

Check if tensorflow is installed properly.
```
python3 -m pip list | grep -i tensor
```

Check if the correct version of tensorflow is installed.
```
python3 -c "import tensorflow as tf; print(tf.__version__)"
```

Check if python and tensorflow recognizes all the GPUs.
```
python3 -c "import tensorflow as tf; print(tf.test.gpu_device_name())"
```

Check if the tensorflow installation is correct by running
```
python3 -c "import tensorflow as tf;print(tf.reduce_sum(tf.random.normal([1000, 1000])))"
```

## Running Deep Press

1. Pull the project from the repository. At the time of writing this documentation, the repository with the tensorflow 2 updates is present in the branch `7-port-to-tf2`.
    ```
    git clone -b 7-port-to-tf2 --single-branch https://github.com/ngcoders/deeppress.git 
    ```
    If everything goes well, this will be merged with the main branch. Then we can use
    ```
    git clone https://github.com/ngcoders/deeppress.git 
    ```

1. Navigate to `deeppress` and install the python packages. 
    ```
    cd deeppress
    python3 -m pip install -r requirements.txt
    ```

1. Copy the deeppress.conf.example to deeppress.conf and edit the latter with the proper configurations.
    ```
    cp deeppress.conf.example deeppress.conf
    nano deeppress.conf
    ```
1.  `[Recommended]` After editing, it is recommended to start the program in such a way that the process will not stop and we get a log file nohup.out.
    ```
    nohup python3 -m deeppress --config=deeppress.conf &
    ```

    `[Not Recommended]` After editing, the another way to start the program is
    ```
    python3 -m deeppress --config=deeppress.conf
    ```

1. We can see the all the debug logs with
    ```
    tail -f nohup.out
    ```

1. The service is available at `http://0.0.0.0:8000`. Please input the IP address of the machine with the designated port value at Deeppress > Settings found at [this link](https://hal.avuity.com/wp-admin/admin.php?page=settings).

## Setting up Wordpress and GuI Login

The Deeppress script is available as a WordPress plugin and needs Wordpress to be installed before we can manage and create models in it. We will use a commonly available wordpress environment setup tool Wordops and use that to install our deeppress plugin inside it. Please make sure no existing Services like nginx mysql exist on the server we are setting this up on.

Installing WordPress base and required services ( this will take a few minutes ) - 
```
wget -qO wo wops.cc && sudo bash wo
```

Now we setup a basic wordpress site, the domain can be a subdomain of a existing domain for example `hal4.avuity.com`. Username and Password can be say `admin` and `password`
```
wo site create hal4.avuity.com --wp --user=admin --pass=password
``` 

Now edit your local hosts file to point to `hal4.avuity.com` and the site should be available in the browser now. 

Now visit the admin section and log into the site by appending wp-admin, so it becomes
```
http://hal4.avuity.com/wp-admin ( Use the password selected above ). 
```

Download the latest release of Deeppress on [this page](https://github.com/ngcoders/deeppress/tree/master/wordpress/plugin/deeppress) and visit the plugins sections > Add new and click upload plugin to install it.Once done Activate the plugin.

After you have setup installed Deeppress visit settings page of deeppress and set the url to point to Deeppress backend and you should be able to start using Deeppress now . The Remote host url should be for ex `http://{ip}:8000`.

If ssl needs to be installed, the site config path should be `/etc/nginx/sites-availbile/{domain.name}`. Wordops support letsencrypt certificates if your domain is available on the cloud.

## Documentation Version History

| Date | Author | Changes |
|:-----|:-------|:--------|
| 2022-10-13 | Allan | Added the documentation to github with minor changes |
| 2022-06-28 | Vikas | Added Wordpress Install Details |
| 2022-06-02 | Allan | Initial Draft for TF2 Release |
