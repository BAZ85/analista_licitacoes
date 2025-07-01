from typing import Optional, List, Dict, Union, Any
from langchain_core.language_models.llms import BaseLLM
from langchain_core.outputs import Generation, LLMResult
from litellm import completion
from pydantic import Field 


class LiteLLMWrapper(BaseLLM):
    model: str
    api_base: str
    api_key: str
    stop: Optional[List[str]] = Field(default=None)

    
    def _call(self, prompt: Union[str, List[Dict[str, str]]], stop: Optional[List[str]] = None) -> str:
        if isinstance(prompt, list):
            messages = prompt
        else:
            messages = [{"role": "user", "content": prompt}]
        
        args = {
            "model": self.model,
            "messages": messages,
            "api_base": self.api_base,
            "api_key": self.api_key,
            "custom_llm_provider": "ollama"
        }    
        
        if stop:
            args["stop"] = stop

        response = completion(**args)
        return response['choices'][0]['message']['content']
    
   
    def _generate(
            self,
            prompts: List[str],
            stop: Optional[List[str]] = None,
        ) -> LLMResult:
            generations = []

            for prompt in prompts:
                text = self._call(prompt, stop=stop)
                generations.append([Generation(text=text)])

            return LLMResult(generations=generations)
    
    
    def call(
            self, 
            prompt: Union[str, List[Dict[str, str]]] = None,
            stop: Optional[List[str]] = None, 
            run_manager: Optional[Any] = None
    ) -> str:
        return self._call(prompt, stop=stop)

    
    def invoke(self, input: Union[str, List[Dict[str, str]]], **kwargs: Any) -> str:
        stop = kwargs.get("stop", self.stop)
        return self._call(input, stop=stop)

    
    @property
    def _llm_type(self) -> str:
        return "litellm-wrapper"

    
    def supports_stop_words(self) -> bool:
        # Marque como True apenas se seu endpoint suporta o parâmetro `stop`
        return False
