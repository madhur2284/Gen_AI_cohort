import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from openai import AsyncOpenAI
from tiktoken import encoding_for_model, get_encoding
load_dotenv()

api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model = os.getenv("MODEL", "gpt-4o-mini")

if not api_key:
    raise ValueError("API_KEY is not set. Please add it to your .env file.")

client = AsyncOpenAI(api_key=api_key, base_url=base_url)
executor = ThreadPoolExecutor(max_workers=2)

prompt = "Tell me what 2+2"

def calculate_tokens(prompt: str):
    tokenizer = ""
    try:
        tokenizer = encoding_for_model(model_name=model)
    except:
        tokenizer = get_encoding("cl100k_base")

    result = tokenizer.encode(prompt)
    return len(result)


async def call_llm(prompt: str):
    prompt.strip()
    loop = asyncio.get_running_loop()
    tokens = await loop.run_in_executor(
        executor,
        calculate_tokens,
        prompt
    )
    if(tokens > 300):
        raise ValueError("Prompt is more than 300 token")

    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_completion_tokens=300,
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(call_llm(prompt=prompt))