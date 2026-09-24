from pydantic import BaseModel,Field,validator
from typing import Optional
from bson import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] =Field(None,alias="_id")
    project_id: str = Field(..., min_length=1)

    @validator('project_id')
    def validate_project_id(cls, v):
        if not v:
            raise ValueError('project_id must not be empty')
        elif not v.isalnum():
            raise ValueError('project_id must be alphanumeric')
        return v

    class Config:
        arbitrary_types_allowed = True
       
    
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[("project_id",1)],
                "name":"project_id_index_1",
                "unique":True                
            }
        ]