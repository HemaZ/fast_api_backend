import logging
from fastapi import APIRouter, BackgroundTasks
from storeapi.tasks import _generate_image_api

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/gen_image", status_code=200)
async def gen_image(promot: str, background_task: BackgroundTasks):
    logger.debug(promot)
    return await _generate_image_api(promot)
