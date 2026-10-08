from .providers import QdrantDBProvider
from .VectorDbInterface import VectorDbInterface
from .VectorDBEnums import VectorDBEnum
from controllers.BaseController import BaseController
class VectorDBProviderFactory:
   def __init__(self,config):
      self.config = config
      self.base_controller= BaseController()
     

    
    def create(self,provider:str):
        if provider == VectorDBEnum.QDRANT.value:
            db_path = self.base_controller.get_database_path(db_name=self.config.VECTOR_DB_BACKEND)
            return QdrantDBProvider(
                db_path=db_path, 
                distance_method=self.config.VECTOR_DB_DISTANCE_METHODS)
        else:
            raise ValueError(f"Unknown database type: {provider}")
