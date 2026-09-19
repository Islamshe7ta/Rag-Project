from fastapi import FastAPI, APIRouter,Depends,UploadFile,status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,Settings
from controllers import DataController
from controllers import ProjectController
from controllers import ProcessController
import aiofiles
from models import ResponseSignal
import logging
from routes.schemas.data import ProcessRequest

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
    file_path,file_id=data_controller.generate_unique_filepath(original_filename=file.filename,project_id=project_id)

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
            "file_id": file_id
        },
    )




@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, request: ProcessRequest):
    # Extract parameters from the request
    file_id = request.file_id
    chunk_size = request.chunk_size
    overlap_size = request.overlap_size
    do_reset = request.do_reset
    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    file_chunks = process_controller.process_file_content(file_content=file_content, file_id=file_id, chunk_size=chunk_size, overlap_size=overlap_size)
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_PROCESSING_FAILED.value,
            },
        )
    return file_chunks



    