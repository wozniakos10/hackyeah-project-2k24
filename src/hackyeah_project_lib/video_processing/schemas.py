video_processing_response_schema = {
    "type": "object",
    "properties": {
        "ton_wypowiedzi": { "type": "string" },
        "mimika": { "type": "string" },
        "gestykulacja": { "type": "string" },
        "emocje": { "type": "string" },
        "hate_speech": { "type": "string" },
        "jakość_nagrania": { "type": "string" },
        "nieprawidłowości": { "type": "string" },
        "szum": { "type": "string" }
    },
    "required": ["ton_wypowiedzi", "mimika", "gestykulacja", "emocje", "hate_speech", "jakość_nagrania", "osoba", "nieprawidłowości", "szum"]
}
