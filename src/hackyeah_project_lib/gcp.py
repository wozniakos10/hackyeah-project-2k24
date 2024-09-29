import vertexai
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
from hackyeah_project_lib.config import settings

AUTH_JSON = {
    "type": "service_account",
    "project_id": settings.GCP_PROJECT_ID,
    "private_key_id": settings.GCP_PRIVATE_KEY_ID,
    "private_key": settings.GCP_PRIVATE_KEY,
    "client_email": settings.GCP_CLIENT_EMAIL,
    "client_id": settings.GCP_CLIENT_ID,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": settings.GCP_CLIENT_X509_CERT_URL,
    "universe_domain": "googleapis.com",
}


def generate() -> None:
    info = AUTH_JSON
    storage_cred = service_account.Credentials.from_service_account_info(info)
    vertexai.init(project="rich-ceiling-437018-b5", credentials=storage_cred)
    model = GenerativeModel(
        "gemini-1.5-pro-002",
    )
    responses = model.generate_content(
        [video1, text1],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    for response in responses:
        print(response.text, end="")


video1 = Part.from_uri(
    mime_type="video/mp4",
    uri="https://hackyeah-mt.s3.amazonaws.com/HY_2024_film_01.mp4",
)
text1 = """Look through each frame in the video carefully and answer the question.
Only base your answers strictly on what information is available in the video attached.
Do not make up any information that is not part of the video and do not be too verbose. """

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]


def send_message_to_gemini(file_url, system_message):
    info = AUTH_JSON
    storage_cred = service_account.Credentials.from_service_account_info(info)
    vertexai.init(project="rich-ceiling-437018-b5", credentials=storage_cred)
    
    model = GenerativeModel("gemini-1.5-pro-002")
    
    video_part = Part.from_uri(
        mime_type="video/mp4",
        uri=file_url,
    )
    
    prompt = f"""{system_message}"""
    
    responses = model.generate_content(
        [video_part, prompt],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False,
    )
    
    return responses.text

