from google import genai
from google.genai import types
import pathlib
import time
import asyncio

import my_token

client = genai.Client(api_key=my_token.GEMINI_API_KEY)

# Retrieve and encode the PDF byte
file_path = pathlib.Path('./pdf/Sessions.pdf')

print(time.strftime("%m/%d/%y %H:%M:%S") + " Loading PDF from " + str(file_path))
# Upload the PDF using the File API
sample_file = client.files.upload(
  file=file_path,
)

async def ask_primus(prompt:str): 
  
  full_prompt = (
    "Answer the question below based on the Sessions.pdf file. "
    "Use the same language of the question to answer. "
    "You MUST keep the response under 1700 characters.\n" + prompt
  )
  try:
    response = await asyncio.to_thread(
      client.models.generate_content,
      model="gemini-2.5-flash",
      contents=[sample_file, prompt]
    )

    if not response.text:
      return "I thought about it, but I couldn't generate a text response."

    return response.text[:1900]
  except Exception as e:
    print(f"Error calling Gemini: {e}")
    return "I encountered an error trying to read the archives."