from google import genai
from google.genai import types
import pathlib
import time
import os
from datetime import datetime, timezone
import asyncio

import my_token

client = genai.Client(api_key=my_token.GEMINI_API_KEY)

def get_session_file(client, local_path, display_name="Sessions_Context"):
  """
  Returns the remote file object.
  Reuses the existing file if it exists and is up-to-date.
  Uploads a new one only if the remote is missing (expired) or older than local.
  """
  
  print(f"Checking status of '{display_name}'...")
  
  # 1. Search for the existing file
  existing_file = None
  for f in client.files.list():
      if f.display_name == display_name:
          existing_file = f
          break

  # 2. Decision Logic
  if existing_file:
      # Check if file is ACTIVE (usable)
      if existing_file.state.name != "ACTIVE":
          print(f"Remote file exists but state is {existing_file.state.name}. Deleting...")
          client.files.delete(name=existing_file.name)
          existing_file = None
      else:
          # Check timestamps to see if we need to update
          # Convert local mtime to UTC aware datetime for comparison
          local_mtime = datetime.fromtimestamp(os.path.getmtime(local_path), tz=timezone.utc)
          remote_ctime = existing_file.create_time
          
          # If local file is OLDER than the upload time, the remote is fresh enough.
          if local_mtime < remote_ctime:
              print(f"Cached file found (expires in <48h): {existing_file.name}")
              return existing_file
          else:
              print("Local file is newer than remote version. Refreshing...")
              client.files.delete(name=existing_file.name)
              existing_file = None

  # 3. Upload (only runs if existing_file is None)
  print(f"Uploading new version: {local_path}...")
  new_file = client.files.upload(
      file=local_path,
      config=types.UploadFileConfig(display_name=display_name)
  )

  # Wait for processing
  while new_file.state.name == "PROCESSING":
      print("Processing...")
      time.sleep(2)
      new_file = client.files.get(name=new_file.name)

  if new_file.state.name != "ACTIVE":
      raise Exception(f"File upload failed: {new_file.state.name}")

  print(f"New file ready: {new_file.uri}")
  return new_file

async def ask_primus(prompt:str): 
  
  full_prompt = (
    "Answer the question below based on the Sessions.pdf file."
    "You must answer using the same language of the question, either Portuguese or English."
    "You must keep the whole response under 1700 characters.\n\nQuestion:"
    "\n" + prompt
  )
  
  session_file = get_session_file(client, './pdf/Sessions.pdf', "Sessions_Context")

  try:
    response = await asyncio.to_thread(
      client.models.generate_content,
      model="gemini-2.5-flash",
      contents=[session_file, prompt]
    )

    if not response.text:
      return "I thought about it, but I couldn't generate a text response."

    return response.text[:1900]
  except Exception as e:
    print(f"Error calling Gemini: {e}")
    return "I encountered an error trying to read the archives."