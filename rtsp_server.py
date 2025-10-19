import cv2
import math
import numpy as np
import os
from urllib.parse import quote
import urllib.request
import threading
from collections import Counter

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
CLASSES = ["person", "car", "truck", "bicycle", "motorbike"]
CONF_THRESHOLD = 0.3
NMS_THRESHOLD = 0.4


class StreamingVideo:
    def __init__(self, base_url:str, user:str, password:str, port:int=554):
        password = quote(password)
        self.rtsp_url = f"rtsp://{user}:{password}@{base_url}:{port}/axis-media/media.amp?videocodec=h264"
        self.open_connection()

        # Motion detection
        self.prev_boxes = []
        self.prev_classes = []
        self.motion_threshold = 5

        # Window control
        self.show_window = True
        self.running = True
        self.user_input = None

        # Load COCO classes
        with open(COCO_NAMES_PATH, "r") as f:
            self.COCO_CLASSES = [line.strip() for line in f.readlines()]

        # Start input listener thread
        threading.Thread(target=self._read_input, daemon=True).start()

    def _read_input(self):
        """Read user input from console to control window."""
        while self.running:
            self.user_input = input().strip().lower()

    def open_connection(self):
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            raise Exception(f"Failed to open connection against {self.rtsp_url}")

    def detect_objects(self, frame):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        layer_names = net.getUnconnectedOutLayersNames()
        detections = net.forward(layer_names)

        boxes, confidences, class_ids = [], [], []
        detected_objects = []

        # Collect detections
        for output in detections:
            for detection in output:
                scores = detection[5:]
                class_id = int(np.argmax(scores))
                confidence = float(scores[class_id])
                cls_name = self.COCO_CLASSES[class_id]

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
            cls_name = self.COCO_CLASSES[class_ids[i]]

            # Reclassify cars/trucks
            if cls_name in ["car", "truck"]:
                aspect_ratio = w_box / h_box
                cls_name = "car" if aspect_ratio > 1.5 else "truck"

            # Check motion
            moved = True
            for prev_box, prev_cls in zip(self.prev_boxes, self.prev_classes):
                if cls_name == prev_cls:
                    dx = abs(x - prev_box[0])
                    dy = abs(y - prev_box[1])
                    if math.hypot(dx, dy) < self.motion_threshold:
                        moved = False
                        break

            if moved:
                detected_objects.append(cls_name)
                self.prev_boxes.append((x, y, w_box, h_box))
                self.prev_classes.append(cls_name)

            # Draw bounding box
            label = f"{cls_name}: {confidences[i]:.2f}"
            cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Limit history
        if len(self.prev_boxes) > 50:
            self.prev_boxes = self.prev_boxes[-50:]
            self.prev_classes = self.prev_classes[-50:]

        if detected_objects:
            counts = Counter(detected_objects)
            print(f"Detected moving objects: {', '.join(f'{k}: {v}' for k, v in counts.items())}")

        return frame

    def show_video(self):
        if not self.cap.isOpened():
            return

        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    continue

                frame = self.detect_objects(frame)

                # Handle user input
                if self.user_input:
                    if self.user_input == 'q':
                        print("Exiting...")
                        self.running = False
                        break
                    elif self.user_input == 'h':
                        self.show_window = False
                        cv2.destroyAllWindows()
                        print("Window hidden. Type 's' to show again.")
                    elif self.user_input == 's':
                        self.show_window = True
                        print("Window shown.")
                    self.user_input = None

                if self.show_window:
                    cv2.imshow("Axis Camera Stream", frame)
                    cv2.waitKey(1)

        except KeyboardInterrupt:
            print("Stream stopped by user")
        finally:
            self.close_connection()

    def close_connection(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()


