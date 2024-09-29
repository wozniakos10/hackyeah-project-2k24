from pydantic import BaseModel


class VideoProcessingResponse(BaseModel):
    speech_tone: str
    face_mimic: str
    gesticulation: str
    emotions: str
    hate_speech: str
    speech_quality: str
    discrepancies: str
    noises: str
    speech_pace: str
    own_suggestions: str
