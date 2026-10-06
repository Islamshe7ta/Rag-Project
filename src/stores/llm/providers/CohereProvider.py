from ..LLMInterface import LLMInterface
from ..LLMEnums import CohereEnums,DocumentType
import cohere
import logging


class CohereProvider(LLMInterface):
    def __init__(self, api_key:str,
                default_input_max_charachters:int=1000,
                default_output_max_charachters:int=1000,
                default_generation_temperature:float=0.1,
                default_embedding_size:int=None,
              ):

        self.api_key = api_key
        self.default_input_max_charachters = default_input_max_charachters
        self.default_output_max_charachters = default_output_max_charachters
        self.default_generation_temperature = default_generation_temperature  
        self.default_embedding_size = default_embedding_size
        self.generation_model_id = generation_model_id
        self.embedding_model_id = embedding_model_id
        self.logger = logging.getLogger(__name__)
        
        self.client = cohere.Client(
            api_key=self.api_key,
        )
    
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        
    def set_embedding_model(self, model_id: str,embedding_size:int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self,text : str ):
        return text[: self.default_input_max_charachters].strip()
        
        
    def generate_text(self, prompt: str,chat_history:list=[] ,max_output_tokens:int=None,temperature:float=None):
                       
            if not self.client:
                self.logger.error("Cohere client is not set")
                return None
            
            if not self.generation_model_id:
                self.logger.error("Cohere generation model id is not set")
                return None

            max_output_tokens =max_output_tokens if max_output_tokens is not None else self.default_output_max_charachters
            temperature =temperature if temperature is not None else self.default_generation_temperature

            response = self.client.chat(
                model=self.generation_model_id,
                chat_history=chat_history,
                message=self.process_text(prompt),
                temperature=temperature ,
                max_tokens=max_output_tokens
            )
            
            
            if not response or not response.text :
                self.logger.error("No response from Cohere API")
                return None
                
            return response.text
    
    def embed_text(self,text:str) :

        if not self.client:
            self.logger.error("Cohere client is not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Cohere embedding model id is not set")
            return None
        
        input_type=CohereEnums.DOCUMENT.value 
        if DocumentType.DOCUMENT.value :
            input_type=CohereEnums.DOCUMENT.value 
        elif DocumentType.QUERY.value:
            input_type=CohereEnums.QUERY.value

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[text],
            input_type=input_type,
            embedding_types=["float"]
        )
        
        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("No response from Cohere API")
            return None
            
        return response.embeddings.float[0]
        
        
    

         
    def construct_prompt(self,prompt:str, role :str) :
        return {
            "role":role,
            "text":self.process_text(prompt)
        }
