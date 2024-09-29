from pydantic import BaseModel


class VideoProcessingResponse(BaseModel):
    ton_wypowiedzi: str
    mimika: str
    gestykulacja: str
    emocje: str
    hate_speech: str
    jakość_nagrania: str
    nieprawidłowości: str
    szum: str
