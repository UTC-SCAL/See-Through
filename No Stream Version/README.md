# US Ignite: Computer Vision Aided Vehicle Detection

When downloading this source / cloning in Git, you must download [this weights file](https://drive.google.com/open?id=0B_IDNqlxDXtKdUw0SEFqNFFlZHM), and put it in a folder you create called "weights" (this folder should be alongside the "examples" folder).

## This is a custom sub-version of the USIgnite code that requires NO intercommunication between multiple client computers; this is only ideal for **testing**!


## Setup:

Setting up a development workspace is a _very specific_ process, so be sure to follow this to the T!

**Required Libraries / Installers:**

- Python 3.5.3
- Anaconda
- CUDA
- OpenCV3
- TensorFlow
- Flask

**Installation Process:**

1. Install Anaconda - **this will include a Python install for you**
2. Run `conda install python=3.5.3`
3. Download and install [CUDA toolkit 8.0](https://developer.nvidia.com/cuda-downloads)

    Do **not** install the driver
4. Download [cuDNN v5.1 for CUDA 8.0](https://developer.nvidia.com/rdp/form/cudnn-download-survey)
5. Extract the cuDNN tarball anywhere, then CD into it

    Run `sudo cp -r * /usr/local/cuda-8.0/`
6. Add the relevant CUDA folders to your PATH via (on Unix / Linux):

    `export CUDA_HOME=/usr/local/cuda`

    `export LD_LIBRARY_PATH=${CUDA_HOME}/lib64`

    `export PATH=${CUDA_HOME}/bin:${PATH}`
7. Install Tensorflow for GPU: `conda install tensorflow-gpu`

8. Install OpenCV3:

    **On Linux:** Run `conda install -c menpo opencv3=3.2.0`

    **On Windows / macOS:** `conda install --channel https://conda.anaconda.org/menpo opencv3`

9. Install Flask: `conda install -c anaconda flask=0.12.2`

Trying to maintain multiple versions of Python is going to be a headache and is not recommended (or necessary).

If you **must** maintain separate environments for your Python projects, I suggest [this guide](https://conda.io/docs/using/envs.html).

All of the project's code is in **Python 3** syntax


## Usage:

After installing all required dependencies, you should have no problems running the clients and server.

Both clients need to be run first via `client.py`. This is so that their HTTP livestream of footage is available to be requested by the server. Once run, client.py will ask which video device it should initialize (if it fails, it defaults to 0).

After both clients are running, the server can be run via `server.py`, which also requires the arguments `IP_Front` and `IP_Rear` - both of which **require** the ports to be included. Once the server is up, the livestream will be available to watch with live YOLO processing. `server.py` will need to be edited to include the correct IPs for the video streams from the clients.


### Credits:

Much of the vehicle detection code is based around an API called [YOLO](https://pjreddie.com/darknet/yolo/).

Our YOLO Pipeline implementation is all thanks to [Junsheng Fu](https://github.com/JunshengFu/autonomous-driving-vehicle-detection), whose code proves to be an invaluable resource at implementing our own uses. Without his code, we would not be able to complete this project to the extent which we have. All changes to his code are documented via GitHub Commit history, and this repository's licensing is a reflection of his.
