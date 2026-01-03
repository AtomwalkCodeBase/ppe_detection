from app.lms.ppe_policy import LAB_PPE_RULES

DISPLAY_NAMES = {
    "mask": "Face Mask",
    "gloves": "Examination Gloves",
    "coat": "Protective Clothing",
    "shield": "Face Shield",
    "shoes": "Shoes Cover"
}

def normalize(label: str):
    label = label.lower()
    if "mask" in label:
        return "mask"
    if "glove" in label:
        return "gloves"
    if "coat" in label or "blouse" in label or "protective" in label:
        return "coat"
    if "shield" in label:
        return "shield"
    if "shoe" in label:
        return "shoes"
    return label

class DecisionEngine:
    def evaluate(self, lab_id: str, detected_objects: list):

        if "person" not in detected_objects:
            return {
                "status": "NO_PERSON",
                "ppe_status": {},
                "overall": "FAILED"
            }

        required = LAB_PPE_RULES.get(lab_id, [])
        detected_norm = {normalize(d) for d in detected_objects}

        ppe_status = {}
        overall_ok = True

        for req in required:
            display = DISPLAY_NAMES.get(req, req)
            if req in detected_norm:
                ppe_status[display] = "PASSED"
            else:
                ppe_status[display] = "FAILED"
                overall_ok = False

        return {
            "status": "PPE_OK" if overall_ok else "PPE_MISSING",
            "ppe_status": ppe_status,
            "overall": "PASSED" if overall_ok else "FAILED"
        }
