from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

prompt = """
    Tell What 2000 + 200000000 is?
    only give answer in the format given in examples.
    Examples:
    - What 3 + 5 is?
        answer: 8(eight)
    - what 9 + 9 is?
        answer: 18(eighteen)
"""

async def zero_shot_prompt(prompt: str):
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
        messages=[{"role": "user", "content": prompt}],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(zero_shot_prompt(prompt))
