from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./podcastr.db"
    SECRET_KEY: str = "supersecretkey_change_this"
    GOOGLE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    TTS_MODEL_PATH: str = ""
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    PRODUCTION: bool = False  # Set to True on Render via env var

    class Config:
        env_file = ".env"

settings = Settings()
