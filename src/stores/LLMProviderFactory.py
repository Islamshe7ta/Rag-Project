from src.helpers.config import get_settings
from src.stores.llm.providers.OpenAiProviders import OpenAiProviders
from src.stores.llm.providers.CohereProvider import CohereProvider
from src.stores.LLMEnums import LLMEnums




class LLMProviderFactory:
    
    def __init__(self,config=dict):
        self.config = config
        
    def create(self, provider: str):
        if provider == LLMEnums.OPENAI.value:
            return OpenAiProviders(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_input_max_charachters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_output_max_charachters=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )
        elif provider == LLMEnums.COHERE.value:
            return CohereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max_charachters=self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_output_max_charachters=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
                default_embedding_size=self.config.EMBEDDING_SIZE_ID
            )
        else:
            raise ValueError(f"Provider type {provider_type} is not supported")
    
    
    
    
    
    