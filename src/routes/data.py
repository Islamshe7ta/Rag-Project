from fastapi import FastAPI, APIRouter,Depends,UploadFile,status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,Settings
from controllers import DataController
from controllers import ProjectController
import aiofiles
from models import ResponseSignal
import logging

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)

@data_router.post("/upload/{{project_id}}")
async def upload_data(project_id: str,
                      file:UploadFile,
                      settings: Settings = Depends(get_settings)
                      ):

#validate file type and size
    data_controller=DataController()
    is_valid,result_signal=data_controller.validate_upload_file(file=file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": result_signal,"allowed_types":settings.FILE_ALLOWED_TYPES,"max_size":settings.FILE_MAX_SIZE}
        )
   
    project_dir_path=ProjectController().get_project_path(project_id=project_id)
    file_path=data_controller.generate_unique_filename(original_filename=file.filename,project_id=project_id)

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error occurred while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value, 
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "file_path": file_path,
            "signal": ResponseSignal.FILE_SUCCESSFULLY_UPLOADED.value,
        },
    )




