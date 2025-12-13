
from metagpt.llm import LLM
instance = LLM()
print(f"Instance class: {instance.__class__}")
print(f"MRO: {instance.__class__.mro()}")

import metagpt.provider.openai_api
print(f"OpenAILLM in module: {metagpt.provider.openai_api.OpenAILLM}")
