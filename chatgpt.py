import openai
from openai import OpenAI
from dotenv import load_dotenv
import requests
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def generate_reply(prompt, model="gpt-3.5-turbo"): #chatgpt
#     try:
#         response = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {"role": "system", "content": "You are a helpful email assistant. Reply professionally and concisely."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         print(f"[OpenAI Error] {e}")
#         return None


def generate_reply(prompt, model="llama3"): #llama3
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False
        })
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        print(f"[Ollama Error] {e}")
        return None