import vertexai
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

AUTH_JSON = {
    "type": "service_account",
    "project_id": "rich-ceiling-437018-b5",
    "private_key_id": "031d3be3beaec8c760d8f51d43055e2f8d988d58",
    "private_key": (
        "-----BEGIN PRIVATE KEY-----"
        "\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCd48pMSZISA6Ji\n"
        "7R82THp9PcLzzWQ9o3nkVr4iMxDQ7ZK7FTxOSBC7yTjLR/ppwaq5HQdUD4p9jFMW\nGmd90mp3dLaUdZkYyngl0xqUV18r"
        "ApdpuYx6AXdT0oBF8mdWxBuhBMusby5UmEfI\nPnFebfidCLa4+90FNjk88/4CUH7WmKfiRxphFss0zDDnWsKgYJg+Jtt8c"
        "E0Ut3a1\nqfKNZUgbcUO0T/re/P+J5MBoUaolOPcxduYzMdFP6bly7z66sEgZhVbIxCmmsVRq\nFpQwdLZkQXOawHE03sMUm"
        "Yfp9RgcnFdNvqx85hS0DmvmYOETXrYuFKTlo7m5GPPK\nd8UVQAhtAgMBAAECggEAGQYoYuzqJMbEru8sGjwG0eC/DEsKTyagx"
        "ArneZ4kVSjC\nL7qO401SsaCTyswuqSJTv6EVL0KDTaC27nLi4jM+Qo6R/Xeh+ybj4gLSXJ54a+Wu\nP8hztkaTNgrP38Yqk"
        "LrmMiADc+HvMuMrxVX4O+IsHB9sbmckwZW1fq6hHJbLc5Fg\nl0JpFVQe3cvrzPg+DftlwF/CVUmEKrt27/MyT3tlqL+y7KD"
        "amIOXyenVTEgNlyqX\nV4stM1Xqpzg7tihPb/fR/bsH/AikUTrx/+bDz/zBvnVSODNiRd6Y0Pb+7EdhO4Gm\nDQU3rV2d/"
        "6SqoC/iEGw1qh5FpZGB4N1mA/cN2VoKlQKBgQDKnYeGtkaqJePRBI9e\nVj5G3okA0voN6CRlz9cJmEpOAhQL2aXOz62Q3mWdb"
        "1qmobDkWGcJg8Ao05jpjP5/\n9XnjQbywdFMz1iHkpqyy6Zk8a8VUk8XLrEHwPO6yinr9u3b17xBfLg/E46YfoEgP\nqKsB3Ks"
        "7c9uOmE69733iQWjjTwKBgQDHfYIsuf1y3Gmz+z4R5E860+8ery77wrpo\n0zzCS6U2xj+TrYS0Uc0SNaXZvvBpZU+ScBsOx"
        "0YiHHgse/xjYBuBhHqmy+kaDDjl\n68PlGmGufINNGk+8/ZYtR7aqmuQ3ienrhRkAt8X8rRKx8WZsNkXUWZiKjFjBtQeo\n"
        "AfCl908ZgwKBgQC0BMqJEiIuwoNrDlYjRxUF+mpXZRvuhzbvjn5MdBZwwL/212XO\nHg7kC/TUsD8mlbqI51KEzZ5Jp9bQiwk"
        "Dv6KQG7P+Qxw5jiOG99+xBoOzfz1QLAst\nLttXC4w47XjhP1IuqD0vk8lG8cyDhPEBmKZ3fQxWQlXsl74+Wy7Je7wpWQKBg"
        "C/E\nuQAWxT7U0qbbWYCVR/eROigB0OFOPq7NLjZkQLp9/ElTenxnPhDHMeCTHSRPsx8g\nowoF46BVat1UDxqIr+1ymKAKI"
        "dYv6Qv9SZo5l/xdKl+zFjbuDiDnlDEEB/PYnV/d\nLiCC4PDhTKG5aUouMMhpb+J1OueffqbXWBWVw6YbAoGAKLxlH6c9ogs"
        "EjH7UyWSv\nxewm2o2JtH1SFnA23knEGbXfBpxp8U4NflQQNGB7JqNS0Jvj3ErLGVBR+/eJCStj\np+OSn/RI5YmqPUEZe9i"
        "ZDBEKVohJE5fkBtRo85By4/RXzEnED7cp85VLr89HBgTK\ntIsWwRmR8bvch/F3zVJ3LJ8="
        "\n-----END PRIVATE KEY-----\n"
    ),
    "client_email": "hackyeah@rich-ceiling-437018-b5.iam.gserviceaccount.com",
    "client_id": "106251336070301551304",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": (
        "https://www.googleapis.com/robot/v1/metadata/x509/hackyeah%40rich-ceiling-437018-b5.iam.gserviceaccount.com"
    ),
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
Do not make up any information that is not part of the video and do not be too verbose.

Questions:
- When does a red lantern first appear and what is written in the lantern? Provide a timestamp.
- What language is the person speaking and what does the person say at that time?"""

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

generate()
