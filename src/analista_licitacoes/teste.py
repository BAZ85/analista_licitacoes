from litellm import completion

response = completion(
    model="llama3.3",
    messages=[{"role": "user", "content": "Olá, quem é você?"}],
    api_base="https://llm.tce.mt.gov.br/v1",
    api_key="any_value",
    custom_llm_provider="openai"
)

print(response['choices'][0]['message']['content'])
