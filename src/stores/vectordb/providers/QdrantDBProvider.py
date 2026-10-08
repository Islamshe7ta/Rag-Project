from qdrant_client import QdrantClient,models
from ..VectorDbInterface import VectorDbInterface
from src.stores.vectordb.VectorDBEnums import VectorDBEnum, DistanceMethodsEnums
import logging 
from typing import List

class QdrantDBProvider(VectorDbInterface):
    def __init__(self,db_path:str, distance_method:str):
        self.client = None
        self.db_path = db_path
        logging.info("QdrantDB initialized")
        self.distance_method = None

        if distance_method == DistanceMethodsEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodsEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        self.logger.info("QdrantDB connected")

    def disconnect(self):
        self.client.close()
        self.logger.info("QdrantDB disconnected")

    def is_collection_exists(self, collection_name: str) -> bool:
       return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self) -> list:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str)->dict:
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str)->bool:
        return self.client.delete_collection(collection_name=collection_name)

    def create_collection(self, collection_name: str,embedding_size:int,do_reset:bool =False)->bool:
        if do_reset:
            self.logger.info(f"Deleting collection {collection_name} if exists")
            _ = self.delete_collection(collection_name=collection_name)
        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.info(f"Creating collection {collection_name}")
            _ = self.client.create_collection(collection_name=collection_name
                                            ,vectors_config=models.VectorParams(
                                                size = embedding_size,
                                                distance = self.distance_method
                                            )
                                        )
            return True
        else:
            self.logger.info(f"Collection {collection_name} already exists")
            return False
    
    def insert_one(self, collection_name: str,
                    text:str,
                    vector:list,
                    metadata:dict,
                    record_id:str = None):

        if not self.is_collection_exists(collection_name=collection_name):
            self.logger.info(f"Collection {collection_name} does not exist")
            return False
        self.logger.info(f"Inserting one document into collection {collection_name}")
        _=self.client.upload_records(collection_name=collection_name,
                                        records=[models.Record(
                                            vector=vector,
                                            payload={
                                                "text":text,
                                                "metadata":metadata
                                            }
                                        )])
        return True
    

    def insert_many(self, collection_name: str,
                    texts:List,
                    vectors:List,
                    metadata:List,
                    record_ids:List = None,
                    batch_size:int = 50):
        
        if metadata is None:
            metadata = [None]*len(texts)

        if record_ids is None:
            record_ids = [None]*len(texts)

        for i in range(0,len(texts),batch_size):
            batch_end = i + batch_size
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_records=[
                models.Record(
                    vector=batch_vectors[x],
                    payload={
                        "text":batch_texts[x],
                        "metadata":batch_metadata[x]
                    }
                ) for x in range(len(batch_texts))
            ]
            try:
                _ =self.client.upload_records(
                                            collection_name=collection_name,
                                            records=batch_records
                                            )
            except Exception as e:
                self.logger.error(f"Error inserting batch: {e}")
        return True

    def search_by_vector(self, collection_name: str,
                            vector:list,
                            limit:int=5,
                           ):
        return self.client.search(collection_name=collection_name,
                                    query_vector=vector,
                                    limit=limit)
    
       
        