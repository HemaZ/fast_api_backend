import tempfile
import logging
from fastapi import APIRouter, HTTPException, UploadFile, status
from storeapi.libs.b2 import b2_upload_file

import aiofiles

logger = logging.getLogger(__name__)

router = APIRouter()

CHUNCK_SIZE = 1024 * 1024


@router.post("/upload", status_code=200)
async def upload_file(file: UploadFile):
    try:
        with tempfile.NamedTemporaryFile() as temp_file:
            filename = temp_file.name
            logger.info(f"Saving upload file to {filename}")
            async with aiofiles.open(filename, "wb") as f:
                while chunck := await file.read(CHUNCK_SIZE):
                    await f.write(chunck)
            file_url = b2_upload_file(local_file=filename, file_name=file.filename)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Uploading file",
        )
    return {"detial": "File uploaded succesfully", "file_url": file_url}
