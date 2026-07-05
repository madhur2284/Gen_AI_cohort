from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

async def zero_shot_prompt():
    base_url = os.getenv("BASE_URL")
    model = os.getenv("MODEL")
    api_key = os.getenv("API_KEY")
    if(model == None):
        raise ValueError("Model is not defined")
    
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url
    )
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "what 2 + 2 is"}],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(zero_shot_prompt())