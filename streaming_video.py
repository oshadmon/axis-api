import cv2
import os
from urllib.parse import quote
import urllib.request
import numpy as np

ROOT_DIR = os.path.dirname(os.path.expanduser(os.path.expandvars(__file__)))
MODELS = os.path.join(ROOT_DIR, 'models')
if not os.path.isdir(MODELS):
    os.makedirs(MODELS, exist_ok=True)

WEIGHTS_PATH = os.path.join(MODELS, "yolov4-tiny.weights")
CFG_PATH = os.path.join(MODELS, "yolov4-tiny.cfg")
if not os.path.isfile(CFG_PATH):
    urllib.request.urlretrieve("https://raw.githubusercontent.com/AlexeyAB/darknet/refs/heads/master/cfg/yolov4-tiny.cfg", CFG_PATH)
if not os.path.isfile(WEIGHTS_PATH):
    urllib.request.urlretrieve('https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights', WEIGHTS_PATH)

# Load YOLOv4-tiny model
net = cv2.dnn.readNet(WEIGHTS_PATH, CFG_PATH)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Target classes
CLASSES = ["person", "car", "truck", "bicycle", "motorbike"]
CONF_THRESHOLD = 0.3
NMS_THRESHOLD = 0.4


class StreamingVideo:
    def __init__(self, base_url:str, user:str, password:str):
        password = quote(password)
        self.rtsp_url = f"rtsp://{user}:{password}@{base_url}:554/axis-media/media.amp?videocodec=h264"
        self.open_connection()

    def open_connection(self):
        try:
            self.cap = cv2.VideoCapture(self.rtsp_url)
            if not self.cap.isOpened():
                raise Exception(f"Failed to open connection against {self.rtsp_url.rsplit(':', 1)} (Error: {error})")
        except Exception as error:
            raise Exception(f"Failed to open connection against {self.rtsp_url.rsplit(':', 1)} (Error: {error})")

    def detect_objects(self, frame):
        """
        Run YOLOv4-tiny detection on a frame and return the frame with bounding boxes.
        Cars and trucks are distinguished based on bounding box aspect ratio.
        """
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        layer_names = net.getUnconnectedOutLayersNames()
        detections = net.forward(layer_names)

        boxes = []
        confidences = []
        class_ids = []

        for output in detections:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                # Only process classes we care about
                if confidence > CONF_THRESHOLD and CLASSES[class_id] in CLASSES:
                    center_x, center_y, width, height = (detection[0:4] * np.array([w, h, w, h])).astype(int)
                    x = int(center_x - width / 2)
                    y = int(center_y - height / 2)

                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Non-Max Suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, CONF_THRESHOLD, NMS_THRESHOLD)

        for i in indices.flatten():
            x, y, w_box, h_box = boxes[i]
            cls_name = CLASSES[class_ids[i]]

            # --- Reclassify cars/trucks based on aspect ratio ---
            if cls_name in ["car", "truck"]:
                aspect_ratio = w_box / h_box
                if aspect_ratio > 1.5:
                    label_name = "car"
                else:
                    label_name = "truck"
            else:
                label_name = cls_name

            label = f"{label_name}: {confidences[i]:.2f}"

            cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame

    def show_video(self):
        if self.cap.isOpened():
            try:
                while True:
                    ret, frame = self.cap.read()

                    # AI program call goes here
                    frame = self.detect_objects(frame)

                    cv2.imshow("", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            except KeyboardInterrupt:
                pass
            finally:
                self.close_connection()

    def close_connection(self):
        if self.cap.isOpened():
            self.cap.release()
            cv2.destroyAllWindows()