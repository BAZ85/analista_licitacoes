from langchain_openai import ChatOpenAI

response = ChatOpenAI(
    model="llama3.3",
    messages=[{"role": "user", "content": "Olá, quem é você?"}],
    base_url="https://llm.tce.mt.gov.br/",
    api_key="any_value",
    
)

print(response['choices'][0]['message']['content'])
