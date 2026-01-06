import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse

def generate_lab_qr(lab_id: str):
    qr = qrcode.make({"lab_id": lab_id})
    buf = BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
