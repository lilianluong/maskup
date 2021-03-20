# Face/Face Mask Detection with YOLO

The baseline code is inherited from [MIAM_FACE_Mask_Yolo](https://github.com/thangnch/MIAI_Face_Mask_YOLO) repo. 

Thank you Mr. Nguyen Chien Thang for your hard work. Because author only provides the face prediction on images. I've added another video implementation code. 

These are some specifications:

* Face Mask Detection: YOLO
* Train/val/test set: `WIDER FACE` and `MAFA` dataset

You can you any video resolution as an input. 

For more information details about Datasets as well as YOLO model, please contact the authors in reference. 

## 1. Requirements

* python==3.6.9
* opencv
* imutils
* hung-utils

## 2. How to install packages
Install my custom packages for reading video and export video

```
pip3 install -i https://test.pypi.org/simple/ hung-utils==0.5.7
```

```
pip3 install -r requirements.txt
```

Install GDOWN to download the pre-trained model
```
pip3 install gdown
```

## 3. Download Pre-trained Model
You need to create `data` folder and download pre-trained YOLO model. Move 2 files `yolo.names` and `yolov3_6000.weights` into `data` folder.
```
mkdir data
gdown --id 10obD7emPjtp00b-pv2GuRw9EIpIPnvYW
gdown --id 1yQgXZslsNJvcfDJcLj-rQm76HPdWSHcY
mv yolo.names data
mv yolov3_6000.weights data
```


## 4. How to run 

On image: 

```
python3 YOLO_img.py --image <img_path>
```

On video: 

```
python3 YOLO_video.py --video <video_folder>
```

## 5. Demo

https://www.youtube.com/watch?v=DS2xdOo69LU

## 6. References

[Article - MIAI - Face Mask Detection ](https://www.miai.vn/2020/04/27/nhan-dien-deo-khau-trang-face-mask-detection-bang-yolo/)

[AIZooTech](https://github.com/AIZOOTech/FaceMaskDetection)

