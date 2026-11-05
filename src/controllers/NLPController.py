from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentType
from typing import List
import json

class NLPController(BaseController):
    def __init__(self, vectordb_client, embedding_client, generation_client, template_parser=None):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()

    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
        
        return json.loads(
            json.dumps(
                collection_info,default=lambda x:x.__dict__
            )
        )
    
    def index_into_vector_db(self, project: Project, chunks: List[DataChunk], 
                             chunks_ids: List[int] = None, do_reset: bool = False):
        # step 1 : get collection name from project 
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        # step 2 : manage items 
        texts = [c.chunk_text for c in chunks]  
        metadata = [c.chunk_metadata for c in chunks]
        vectors = [
            self.embedding_client.embed_text(
                text=text,
                document_type=DocumentType.DOCUMENT
            ) for text in texts
        ]
        
        # step 3 : create collection if not exists
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            do_reset=do_reset,
            embedding_size=self.embedding_client.embedding_size
        )
        
        # step 4 : insert into vector db
        record_ids = chunks_ids if chunks_ids is not None else [str(c.id) for c in chunks]
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadata=metadata,
            record_ids=record_ids
        )

        return True
               
        
        
    def search_vector_db_collection(self,project:Project,text:str,limit:int=10):
        collection_name = self.create_collection_name(project_id=project.project_id)
        vector = self.embedding_client.embed_text(
            text=text,
            document_type=DocumentType.QUERY.value
        )
        if not vector or len(vector) == 0:
            return False
        
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )
        if not results or len(results) == 0:
            return False
            
        return results

    def answer_rag_question(self,project:Project,query:str,limit:int=10):
        #steps 1 : retrieve relative doc

        retrieved_docs = self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit
        )
        if not retrieved_docs or len(retrieved_docs) == 0:
            return "I don't have enough information to answer this question."
        
        #steps 2 : construct llm prompt
        system_prompt = self.template_parser.get(
            "rag",
            "system_prompt",
            {
                "query": query,
                "retrieved_docs": retrieved_docs
            }
        )

        #construct documents prompts
        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_num": idx + 1,
                "chunk_text": doc.text,
            })
            for idx, doc in enumerate(retrieved_docs)
        ])


        footer_prompt = self.template_parser.get(
            "rag",
            "footer_prompt",
            {
                "query": query,
                "retrieved_docs": retrieved_docs
            }
        )

        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt="\n\n".join([
            documents_prompts,
            footer_prompt
        ])

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history,
        )

        return answer , full_prompt,chat_history


