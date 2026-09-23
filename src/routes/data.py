from fastapi import FastAPI, APIRouter,Depends,UploadFile,status,Request
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
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(request : Request ,project_id: str,
                      file:UploadFile,
                      settings: Settings = Depends(get_settings)
                      ):
    project_model = ProjectModel (
        db_client = request.app.db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)

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
            "signal": ResponseSignal.FILE_SUCCESSFULLY_UPLOADED.value,
            "file_id": file_id,
           
        },
    )




@data_router.post("/process/{project_id}")
async def process_endpoint(
    project_id: str, 
    process_request: ProcessRequest, 
    app_request: Request
):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = ProjectModel(
        db_client=app_request.app.db_client
    )
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    file_chunks = process_controller.process_file_content(
        file_content=file_content, 
        file_id=file_id, 
        chunk_size=chunk_size, 
        overlap_size=overlap_size
    )

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_PROCESSING_FAILED.value,
            },
        )

    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project.id
        )
        for i, chunk in enumerate(file_chunks)
    ]

    chunk_model = ChunkModel(db_client=app_request.app.db_client)

    if do_reset ==1:
        _= await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )
    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.FILE_PROCESSED_SUCCESSFULLY.value if hasattr(ResponseSignal, "FILE_PROCESSED_SUCCESSFULLY") else "FILE_PROCESSED_SUCCESSFULLY",
            "inserted_chunks": no_records
        }
    )