
from langchain_ollama import ChatOllama

llm = ChatOllama(
    base_url="https://llm.tce.mt.gov.br",
    model="llama3.3"
)

print(llm.invoke("Qual o papel do Tribunal de Contas no Brasil?"))
