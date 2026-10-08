from abc import ABC, abstractmethod

class VectorDbInterface(ABC):
   @abstractmethod
   def connect(self):
    pass

   @abstractmethod
   def disconnect(self):
    pass

   @abstractmethod
   def is_collection_exists(self, collection_name: str) -> bool:
    pass

    @abstractmethod
    def list_all_collections(self) -> list[str]:
        pass

    @abstractmethod
    def create_collection(self, collection_name: str,
                            embedding_size:int,
                           do_reset:bool =False):
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

   @abstractmethod
   def get_collection_info(self, collection_name: str):
    pass

    @abstractmethod
    def insert_one(self, collection_name: str,
                    text:str,
                    vector:list,
                    metadata:dict,
                    record_id:str = None):
     pass

    @abstractmethod
    def insert_many(self, collection_name: str,
                    texts:List,
                    vectors:List,
                    metadata:List,
                    record_ids:List = None,
                    batch_size:int = 50):
     pass
    
    @abstractmethod
    def search_by_vector(self, collection_name: str,
                        vector:list,
                        limit:int,
                       ):
        pass

   