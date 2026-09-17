from .BaseController import BaseController
from fastapi import UploadFile
from models.enums.ResponseEnums import ResponseSignal
import os

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
   

    def get_project_path(self, project_id: str):
        # Construct the project path based on the project_id
        project_dir = os.path.join(
            self.file_dir,
             project_id
        )
        if not os.path.exists(project_dir):
                os.makedirs(project_dir)
        return project_dir

