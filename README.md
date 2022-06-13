# Video labeller

GUI to label adt/anytimer videos to identify the person in the video and the type of adt.

## How to install
Dependencies can be installed with pip:

```
pip install ffpyplayer opencv-python PyQt5
```

## How to use
The GUI needs to be given a path to a folder in which `.mp4` files can be found that need to be labelled. 

``` 
python labeller.py <path_to_mp4_folder>
```

For example, if you have the following folder structure:

```
.
├── ...
├── video_labeller
│   ├── labeller.py          
│   └── ...                
├── videos         
|   └── april_2020
|       ├── whatsapp_video_1.mp4
|       ├── whatsapp_video_2.mp4
|       ├── ...
|       └── whatsapp_video_xxx.mp4
└── ...
```
You can run the GUI from within the `video_labeller/` folder as:
```
    python labeller.py ../videos/april_2020
``` 
