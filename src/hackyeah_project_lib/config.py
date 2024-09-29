from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    S3_BUCKET_NAME: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
    GCP_PROJECT_ID: str
    GCP_PRIVATE_KEY_ID: str
    GCP_PRIVATE_KEY: str
    GCP_CLIENT_EMAIL: str
    GCP_CLIENT_ID: str
    GCP_CLIENT_X509_CERT_URL: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()  # type: ignore
