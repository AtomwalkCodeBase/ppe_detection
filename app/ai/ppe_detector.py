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

PPE_CLASS_MAP = {
    0: "Doctor Blouse",
    1: "Examination Gloves",
    2: "Face Mask",
    3: "Face Shield",
    4: "Protective Clothing",
    5: "Shoes Cover"
}

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
            if self.person_model.names[int(box.cls[0])] != "person":
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if not self._person_intersects_door(x1, y1, x2, y2):
                continue

            detection_result["person_detected"] = True

            cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(
                annotated,
                "Person",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )

            person_crop = frame[y1:y2, x1:x2]
            if person_crop.size == 0:
                break

            ppe_results = self.ppe_model(person_crop, conf=0.5, verbose=False)[0]

            for pbox in ppe_results.boxes:
                cls_id = int(pbox.cls[0])
                conf = float(pbox.conf[0])

                if conf < 0.5:
                    continue

                ppe_label = PPE_CLASS_MAP.get(cls_id)
                if not ppe_label:
                    continue

                if ppe_label not in detection_result["ppe_detected"]:
                    detection_result["ppe_detected"].append(ppe_label)

                px1, py1, px2, py2 = map(int, pbox.xyxy[0])
                fx1 = x1 + px1
                fy1 = y1 + py1
                fx2 = x1 + px2
                fy2 = y1 + py2

                cv2.rectangle(
                    annotated,
                    (fx1, fy1),
                    (fx2, fy2),
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    annotated,
                    ppe_label,
                    (fx1, fy1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 0),
                    2
                )

            break

        return detection_result, annotated
