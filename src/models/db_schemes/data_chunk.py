from pydantic import BaseModel,Field,validator
from typing import Optional
from bson import ObjectId


class DataChunk(BaseModel):
    id: Optional[ObjectId] =Field(None,alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict = Field(..., min_length=1)
    chunk_order: int = Field(..., ge=0)
    chunk_project_id: ObjectId 
    

    
    @validator('chunk_text')
    def validate_chunk_text(cls, v):
        if not v:
            raise ValueError('Fields must not be empty')
        return v

    class Config:
        arbitrary_types_allowed = True