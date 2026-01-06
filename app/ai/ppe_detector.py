from ultralytics import YOLO
import cv2
import numpy as np
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

MODELS_DIR = os.path.join(BASE_DIR, "models")

PERSON_MODEL_PATH = os.path.join(MODELS_DIR, "yolo11n.pt")
PPE_MODEL_PATH = os.path.join(MODELS_DIR, "best.pt")

DOOR_ROI = np.array(
    [
        (566, 3),
        (942, 3),
        (919, 563),
        (562, 594)
    ],
    dtype=np.int32
)

class PPEDetector:
    def __init__(self):
        self.person_model = YOLO(PERSON_MODEL_PATH)
        self.ppe_model = YOLO(PPE_MODEL_PATH)

    def _person_intersects_door(self, x1, y1, x2, y2):
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        return cv2.pointPolygonTest(DOOR_ROI, (cx, cy), False) >= 0

    def detect(self, frame):
        detection_result = {
            "person_detected": False,
            "ppe_detected": []
        }

        annotated = frame.copy()
        person_results = self.person_model(frame, conf=0.5, verbose=False)[0]

        for box in person_results.boxes:
            label = self.person_model.names[int(box.cls[0])]
            if label != "person":
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            if not self._person_intersects_door(x1, y1, x2, y2):
                continue

            detection_result["person_detected"] = True
            person_crop = frame[y1:y2, x1:x2]
            if person_crop.size == 0:
                break

            ppe_results = self.ppe_model(person_crop, conf=0.25, verbose=False)[0]
            for pbox in ppe_results.boxes:
                ppe_label = self.ppe_model.names[int(pbox.cls[0])]
                if ppe_label not in detection_result["ppe_detected"]:
                    detection_result["ppe_detected"].append(ppe_label)

            break

        return detection_result, annotated
