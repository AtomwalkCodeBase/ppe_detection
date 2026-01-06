from app.lms.ppe_policy import LAB_PPE_RULES

PPE_NORMALIZATION = {
    "Face Mask": "mask",
    "Mask": "mask",
    "Examination Gloves": "gloves",
    "Gloves": "gloves",
    "Protective Clothing": "coat",
    "Face Shield": "shield",
}

def normalize(label: str):
    label = label.lower()
    if "mask" in label:
        return "mask"
    if "glove" in label:
        return "gloves"
    if "helmet" in label:
        return "helmet"
    if "shield" in label:
        return "shield"
    if "coat" in label or "gown" in label:
        return "coat"
    return label


class DecisionEngine:
    def evaluate(self, lab_id: str, detected_objects: list):

        if "person" not in detected_objects:
            return {
                "status": "NO_PERSON",
                "ppe_status": {},
                "overall": "FAILED"
            }

        required_raw = LAB_PPE_RULES.get(lab_id, [])
        detected_norm = {normalize(d) for d in detected_objects}

        ppe_status = {}
        overall_ok = True

        for ppe in required_raw:
            norm = normalize(ppe)
            if norm in detected_norm:
                ppe_status[ppe] = "PASSED"
            else:
                ppe_status[ppe] = "FAILED"
                overall_ok = False

        return {
            "status": "PPE_OK" if overall_ok else "PPE_MISSING",
            "ppe_status": ppe_status,
            "overall": "PASSED" if overall_ok else "FAILED"
        }
