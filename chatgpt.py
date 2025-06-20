import openai
from openai import OpenAI
from dotenv import load_dotenv
import requests
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
