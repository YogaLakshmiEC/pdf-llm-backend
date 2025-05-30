from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class PdfUpload(BaseModel):
    doc_id: Optional[str]
    pdf_name: str
    upload_time: datetime
    text: Optional[str] = None

