from pydantic import BaseModel


class IngestPayload(BaseModel):
    entry_id: str
    tenant_id: str
    lab_id: str
    image_base64: str
