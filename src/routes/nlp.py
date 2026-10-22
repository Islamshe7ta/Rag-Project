from fastapi import FastAPI, APIRouter,Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
from routes.schemas.nlp import PushRequest
from models.ProjectModel import ProjectModel 
from models.ChunkModel import ChunkModel
from controllers.NLPController import NLPController
from models.enums.ResponseEnums import ResponseSignal
import os
import logging

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request:Request,project_id: str,push_request:PushRequest):
    project_model = await ProjectModel.create_instance(
        db_client=request.app.state.db_client
    )
    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.state.db_client
    )
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )
    
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message":ResponseSignal.PROJECT_NOT_FOUND.value}
        )
    nlp_controller = NLPController(
        embedding_client=request.app.state.embedding_client,
        vectordb_client=request.app.state.vectordb_client,
        generation_client=request.app.state.generation_client
    )
    page_no = 1
    has_records = True
    inserted_items_count = 0
    idx = 0
    while has_records:
        page_chunks = await chunk_model.get_project_chunks(
            project_id=project.id,
            page_no=page_no,
            page_size=push_request.page_size
        )

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break
        
        chunks_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        # Only reset on the first page if requested
        do_reset = bool(push_request.do_reset) if page_no == 1 else False

        is_inserted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            chunks_ids=chunks_ids,
            do_reset=do_reset
        )
        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.INSERT_INTO_VECTOR_DB_FAILED.value}
            )
        
        inserted_items_count += len(page_chunks)
        page_no += 1

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTOR_DB_SUCCESSFULL.value,
            "inserted_items_count": inserted_items_count
        }
    )
