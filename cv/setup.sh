#!/bin/bash
pip3 install -i https://test.pypi.org/simple/ hung-utils==0.5.7
pip3 install -r requirements.txt
pip3 install gdown
mkdir data
gdown --id 10obD7emPjtp00b-pv2GuRw9EIpIPnvYW
gdown --id 1yQgXZslsNJvcfDJcLj-rQm76HPdWSHcY
mv yolo.names data
mv yolov3_6000.weights data