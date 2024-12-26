from fastapi import UploadFile, HTTPException, status
import os
import aiofiles
from uuid import uuid4

from ..utils.logger_handler import logger


async def upload_image_handler(image: UploadFile, upload_dir: str = "static/images/") -> str:
    # Check if upload directory exists, if not, create it
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Validate image file type based on the file extension
    allowed_extensions = ["jpeg", "png", "jpg"]
    file_extension = os.path.splitext(image.filename)[1].lower().strip('.') #type:ignore

    if file_extension not in allowed_extensions:
        logger.warning(f"Invalid file extension: {file_extension}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image type. Only JPEG, PNG, JPG are allowed."
        )

    # Generate a unique filename to avoid conflicts
    unique_filename = f"{uuid4()}.{file_extension}"
    file_location = os.path.join(upload_dir, unique_filename)

    try:
        # Save the image asynchronously
        async with aiofiles.open(file_location, "wb") as file:
            content = await image.read()
            await file.write(content)

        logger.info(f"Image successfully uploaded: {file_location}")
    except Exception as e:
        logger.error(f"Error saving image {image.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save image: {e}"
        )

    return unique_filename
