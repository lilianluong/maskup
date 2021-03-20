import time
import cv2
import argparse
import numpy as np
import math
import imutils
from videos.utils import *

def get_output_layers(net):

    layer_names = net.getLayerNames()

    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])

    color = COLORS[class_id]

    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)

    cv2.putText(img, label + ': ' + str(round(confidence,2)), (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def run(frame):
    Width = frame.shape[1]
    Height = frame.shape[0]


    # create input blob
    blob = cv2.dnn.blobFromImage(frame, scale, (416,416), (0,0,0), True, crop=False)

    # set input blob for the network
    net.setInput(blob)

    # run inference through the network and gather predictions from output layers
    outs = net.forward(get_output_layers(net))

    # initialization
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4

    start = time.time() 

    # for each detetion from each output layer get the confidence, class id, 
    # bounding box params and ignore weak detections (confidence < 0.5)
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    # apply non-max suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    # go through the detections remaining after nms and draw bounding box
    for i in indices:
        i = i[0]
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]

        draw_prediction(frame, class_ids[i], confidences[i], round(x), round(y), round(x + w), round(y + h))

    end = time.time()
    print("[INFO] YOLO Execution time: " + str(end-start))


    return frame


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--video', required=True,
                    help='path to input video folder')
    ap.add_argument('-c', '--config', default="cfg/yolov3.cfg",
                    help='path to yolo config file')
    ap.add_argument('-w', '--weights', default="data/yolov3_6000.weights",
                    help='path to yolo pre-trained weights')
    ap.add_argument('-cl', '--classes', default="data/yolo.names",
                    help='path to text file containing class names')
    ap.add_argument('-e', '--is_export', default=True, type = bool,
                    help='export the video or not')
    ap.add_argument('-k', '--keep_original_size', default=False, type = bool,
                    help='keep the original size of video or not')
    args = ap.parse_args()

    # Hyperparameters
    scale = 0.00392
    classes = None
    COLORS = [(0,255,0),(0,0,255)]
    video_path = args.video
    keep_original_size = args.keep_original_size
    export_video = args.is_export

    with open(args.classes, 'r') as f:
        classes = [line.strip() for line in f.readlines()]

    video_list = get_videos_list(args.video)
    print ("[INFO] Number of videos: ",len(video_list))
    assert len(video_list) != 0

    # Load models
    net = cv2.dnn.readNet(args.weights, args.config)

    for video in video_list:
        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4
        frame_cnt = 0

        print (f"[INFO] Process: {video}")
        
        capture = cv2.VideoCapture(video)
        hasFrame, image = capture.read()
        frame_cnt = 0 
        H, W = image.shape[:2]

        video_name = video.split('/')[-1].split('.')[0]
        fps = math.ceil(capture.get(cv2.CAP_PROP_FPS))

        while hasFrame:
            if keep_original_size:
                img_height, img_width = H,W
            else:
                image = imutils.resize(image, width= min(720,image.shape[1]))
                img_height, img_width = image.shape[:2]

            if frame_cnt == 0:
                if export_video:
                    writer = prepare_export_video(video_path, video_name, fps, (img_width, img_height))

            # inference
            processed_frame = run(image)

            cv2.imshow("DEBUG MODE - " + video_name, processed_frame)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            if key & 0xFF == ord('s'): # stop
                cv2.waitKey(0)

            if export_video:
                writer.write(processed_frame)

            hasFrame, image = capture.read()
            frame_cnt +=1


        cv2.destroyAllWindows()

        # Export result videos
        if export_video:
            writer.release()