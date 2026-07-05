from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import asyncio
import json5 as json
import httpx
import subprocess

load_dotenv()

async def get_weather(city: str):
    async with httpx.AsyncClient() as client:
        try:
            report = await client.get(url=f"https://wttr.in/{city}?format=%c+%t")
            report.raise_for_status()
            return report.text
        except Exception as e:
            print(f"Error: {e}")


async def exec_cmd(cmd: str):
    result = subprocess.run(cmd, text=True, shell=True, capture_output=True)
    return result.stdout if result.returncode == 0 else result.stderr

func = {
    "get_weather": get_weather,
    "exec_cmd": exec_cmd
}

system_prompt = """
    You are an intelligent assistant. Analyze the user's request, break the problem into smaller steps, solve each step carefully, and return the answer one step at a time.

    Follow this pipeline:
    - INITIAL: Understand the user's intent and the problem.
    - THINK: Break the problem into subproblems.
    - ANALYZE: Solve each subproblem and verify it.
    - TOOL_REQUEST: Call functions when needed.
    - OUTPUT: Provide the final answer.

    Available Tools:
    - get_weather: this tool fetch weather of any city. it's input parameter is city of string type.
    - exec_cmd: this tool execute the CLI Commands for windows. it's input parameter is cmd of string type.

    Return the output in this format:
    '{"step": "INITIAL" | "THINK" | "ANALYZE" | "TOOL_REQUEST" | "OUTPUT", "output": "your output for that step" , "function_name": <function_name>, "input": <input parameter>}'

    Rules:
    - Give one step at a time.
    - Only return the specified format.
    - Return only a single valid JSON object and nothing else.
    - Do not wrap the JSON in markdown code fences.
    - The value of "output" must be a short plain text string with no newlines, quotes, or backslashes.
    - Call functions when it's needed.
    - Use the pipeline for every problem.

    Example:
    Question: What is 6 + 9 * 4 / 5 - 8 * 7 + 9?
    - INITIAL: The user wants a step-by-step arithmetic solution using BODMAS.
    - THINK: Solve the multiplication and division first.
    - ANALYZE: The simplified expression becomes 6 + 7.2 - 56 + 9.
    - THINK: Now solve the remaining addition and subtraction.
    - OUTPUT: The final answer is -33.8.

    Question: What is weather in delhi?
    - INITIAL: The user want information about weather in delhi
    - THINK: We have a Tool called get_weather with input parameter city of type str
    - ANALYZE: This tool will return weather of city so it's right choice.
    - TOOL_REQUEST: call tool get_weather with input parameter delhi.
    - THINK: Tool return 🔆+32°C
    - ANALYZE: This is correct answer to the asked question.
    - OUTPUT: Delhi is sunny today with 32°C.

    Question: Make a txt file with name weather and write delhi: +32°C in it.
    - INITIAL: The user want to make a file and write some text in it.
    - THINK: For creating file and writing in it we have to execute commands in cli. We have a tool called exec_cmd which run cli commands with input parameter cmd of type string
    - ANALYZE: Yes Executing cli commands can do this task.
    - TOOL_REQUEST: call exec_cmd with input 'echo delhi: 32°C> weather.txt'
    - THINK: Tool return file created
    - OUTPUT: weather.txt created and delhi: +32°C written in it.
"""
user_prompt = "What is weather in mumbai and write the output on a beatifull webpage. create a folder named weather in the current directory. Then create index.html, style.css inside that folder. After that, open index.html in the browser using the correct Windows command.”"

message: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


async def chain_of_thought_prompt(message: list):
    base_url = os.getenv("BASE_URL")
    model = os.getenv("MODEL")
    api_key = os.getenv("API_KEY")
    if(model == None):
        raise ValueError("Model is not defined")
    
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url
    )
    while(True):
        response = await client.chat.completions.create(
            model=model,
            messages= message,
        )
        content = response.choices[0].message.content
        result = {}
        try:
            result = json.loads(content)
        except Exception as e:
            message.append({"role": "user", "content": "previous output was not in json format. retry and return output in strict json format"})
            continue
        
        message.append({"role": "assistant", "content": content})

        print(f"🤖({result['step']}): {result['output']}")

        if(result["step"] == "TOOL_REQUEST"):
            ans = await func[result["function_name"]](result["input"])
            message.append({"role": "developer", "content": json.dumps({"step": "THINK", "content" :ans})})
        
        if(result["step"] == "OUTPUT"):
            break


if __name__ == "__main__":
    asyncio.run(chain_of_thought_prompt(message))
