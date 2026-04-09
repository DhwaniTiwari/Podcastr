import cloudinary
import cloudinary.uploader
from app.config import settings

def _configure():
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )

def upload_image(file_bytes: bytes, filename: str) -> str | None:
    """Upload image bytes to Cloudinary and return the secure URL."""
    if not settings.CLOUDINARY_CLOUD_NAME:
        return None  # Cloudinary not configured, fall back to local
    
    _configure()
    try:
        result = cloudinary.uploader.upload(
            file_bytes,
            folder="podcastr",
            public_id=filename.rsplit(".", 1)[0],   # strip extension
            overwrite=True,
            resource_type="image"
        )
        return result.get("secure_url")
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        return None
