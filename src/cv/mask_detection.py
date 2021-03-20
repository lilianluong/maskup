import time
import cv2
import argparse
import numpy as np

CONFIG = "cfg/yolov3.cfg"
WEIGHTS = "data/yolov3_6000.weights"
CLASSES = ["face", "face_mask"]

net = cv2.dnn.readNet(WEIGHTS, CONFIG)


def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers


def detect(image):
    """
    Detect all faces in an image and classifies them as masked or unmasked

    Input: numpy array (height, width, 3) - BGR
    Output: List of tuples (masked, x, y, x+w, y+h)
        masked is a boolean and coordinates are integers
    """
    t0 = time.time()
    width = image.shape[1]
    height = image.shape[0]
    scale = 0.00392

    blob = cv2.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)
    # blob = cv2.dnn.blobFromImage(image, scale, (1024, 1024), (0, 0, 0), True, crop=False)

    net.setInput(blob)

    outs = net.forward(get_output_layers(net))

    class_ids = []
    confidences = []
    boxes = []
    output_tuples = []
    conf_threshold = 0.5
    nms_threshold = 0.4
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > conf_threshold:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
                output_tuples.append((bool(class_id), x, y, x + w, y + h))

    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    output = [output_tuples[i[0]] for i in indices]
    return output
