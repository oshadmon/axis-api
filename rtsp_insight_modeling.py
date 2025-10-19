import cv2
import math
import numpy as np
import os
import urllib.request

ROOT_DIR = os.path.dirname(os.path.expanduser(os.path.expandvars(__file__)))
MODELS = os.path.join(ROOT_DIR, 'models')
if not os.path.isdir(MODELS):
    os.makedirs(MODELS, exist_ok=True)

WEIGHTS_PATH = os.path.join(MODELS, "yolov4-tiny.weights")
CFG_PATH = os.path.join(MODELS, "yolov4-tiny.cfg")
COCO_NAMES_PATH = os.path.join(MODELS, "coco.names")

# Download files if missing
if not os.path.isfile(CFG_PATH):
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/AlexeyAB/darknet/refs/heads/master/cfg/yolov4-tiny.cfg",
        CFG_PATH
    )
if not os.path.isfile(WEIGHTS_PATH):
    urllib.request.urlretrieve(
        'https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights',
        WEIGHTS_PATH
    )
if not os.path.isfile(COCO_NAMES_PATH):
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names",
        COCO_NAMES_PATH
    )

# Load YOLOv4-tiny model
net = cv2.dnn.readNet(WEIGHTS_PATH, CFG_PATH)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Target classes
CLASSES = [
    "person",      # humans
    "car",         # vehicles
    "truck",       # vehicles
    "bus",         # vehicles
    "bicycle",     # vehicles
    "motorbike",   # vehicles
    "dog",         # pets
    "cat",         # pets
    "sports ball"  # for objects like balls
]

CONF_THRESHOLD = 0.3
NMS_THRESHOLD = 0.4
with open(COO_NAMES_PATH, "r") as f:
    COCO_CLASSES = [line.strip() for line in f.readlines()]



def detect_objects(frame:np.ndarray):
    """
    Detect object(s) on screen
    """
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_names = net.getUnconnectedOutLayersNames()
    detections = net.forward(layer_names)

    boxes, confidences, class_ids = [], [], []
    detected_objects = []

    prev_boxes = []
    prev_classes = []
    motion_threshold = 5

    # Collect detections
    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = int(np.argmax(scores))
            confidence = float(scores[class_id])
            cls_name = COCO_CLASSES[class_id]

            if confidence > CONF_THRESHOLD and cls_name in CLASSES:
                cx, cy, bw, bh = (detection[0:4] * np.array([w, h, w, h])).astype(int)
                x = int(cx - bw / 2)
                y = int(cy - bh / 2)

                boxes.append([x, y, int(bw), int(bh)])
                confidences.append(confidence)
                class_ids.append(class_id)

    # Non-Max Suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, CONF_THRESHOLD, NMS_THRESHOLD)
    if indices is not None and len(indices) > 0:
        if isinstance(indices, np.ndarray):
            indices = indices.flatten()
        else:
            indices = [i[0] if isinstance(i, (list, tuple, np.ndarray)) else i for i in indices]
    else:
        indices = []

    # Loop through selected boxes
    for i in indices:
        x, y, w_box, h_box = boxes[i]
        cls_name = COCO_CLASSES[class_ids[i]]

        # Reclassify cars/trucks
        if cls_name in ["car", "truck"]:
            aspect_ratio = w_box / h_box
            cls_name = "car" if aspect_ratio > 1.5 else "truck"

        # Check motion
        moved = True
        for prev_box, prev_cls in zip(prev_boxes, prev_classes):
            if cls_name == prev_cls:
                dx = abs(x - prev_box[0])
                dy = abs(y - prev_box[1])
                if math.hypot(dx, dy) < motion_threshold:
                    moved = False
                    break

        if moved:
            detected_objects.append(cls_name)
            prev_boxes.append((x, y, w_box, h_box))
            prev_classes.append(cls_name)

        # Draw bounding box
        label = f"{cls_name}: {confidences[i]:.2f}"
        cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Limit history
    if len(prev_boxes) > 50:
        prev_boxes = prev_boxes[-50:]
        prev_classes = prev_classes[-50:]

    """
    # Phase 2: add code - if object then generate insights 
    if object: 
        ...
    """
    return frame