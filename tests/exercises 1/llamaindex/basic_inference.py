import os
from llama_index.core.llms import ChatMessage
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai_like import OpenAILike

MODEL = 'qwen3:8b'
API_KEY = os.getenv("VISTEON_OLLAMA_TOKEN")

client = Ollama(MODEL, request_timeout=600)

response = client.chat(messages=[
    ChatMessage(role="system", content="/no_think\nYou are a helpful assistant."),
    ChatMessage(role="user", content='Hi! How are you?')
])
print(response.message.content)

print('--------------------------------------------------------------------')

client = OpenAILike(
    model=MODEL, api_base='http://chipd120.vistcorp.ad.visteon.com:8000/v1', api_key=API_KEY, timeout=600,
    is_chat_model=True, is_function_calling_model=True
)

response = client.chat(messages=[
    ChatMessage(role="system", content="/no_think\nYou are a helpful assistant."),
    ChatMessage(role="user", content='Hi! How are you?')
])
print(response.message.content)

print('--------------------------------------------------------------------')

query = 'My name is Marco'
print('User: '+query)
response = client.chat(messages=[
    ChatMessage(role="system", content="/no_think\nYou are a helpful assistant."),
    ChatMessage(role="user", content= query)
])
print('Assistant: '+response.message.content)

query = 'Do you recall my name?'
print('User: '+query)
response = client.chat(messages=[
    ChatMessage(role="system", content="/no_think\nYou are a helpful assistant."),
    ChatMessage(role="user", content= query)
])
print('Assistant: '+response.message.content)

print('--------------------------------------------------------------------')

query = 'My name is Marco'
print('User: '+query)
messages =[
    ChatMessage(role="system", content="/no_think\nYou are a helpful assistant."),
    ChatMessage(role="user", content= query)
]
response = client.chat(model=MODEL, messages=messages)
messages.append(response.message)
print('Assistant: '+response.message.content)

query = 'Do you recall my name?'
print('User: '+query)
messages.append(ChatMessage(role="user", content= query))
response = client.chat(model=MODEL, messages=messages)
print('Assistant: '+response.message.content)

print('--------------------------------------------------------------------')

gen = client.stream_chat(messages=[
    ChatMessage(role="system", content="/no_think\nYou are a helpful assistant."),
    ChatMessage(role="user", content='Generate a function in python that return true if the provided number is a prime number')
])
for response in gen:
    print(response.delta, end="")

print('\n--------------------------------------------------------------------')
