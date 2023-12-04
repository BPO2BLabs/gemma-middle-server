from flask import Blueprint, request, jsonify
from src.utils.WhisperAI import WhisperAI
import os
import boto3
import json
import uuid
from dotenv import load_dotenv
import requests
import jwt
import time

load_dotenv()

main = Blueprint('transcript_blueprint', __name__)

BACKEND_SECRET_KEY = os.getenv('BACKEND_SECRET_KEY')

AUDIO_FOLDER = os.path.join("/home","ubuntu",".tmpaud")
S3_BUCKET = os.getenv('BUCKET_NAME')
S3_KEY = os.getenv('ACCESS_KEY_ID')
S3_SECRET = os.getenv('ACCESS_SECRET_KEY')
session = boto3.Session(
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET
)
s3_session = session.client('s3')
s3_resource = session.resource('s3')
s3_client = boto3.client('s3', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)

ID_API = os.getenv('ID_API')
BEARER = os.getenv('BEARER')
url_runpod = f"https://api.runpod.ai/v2/{ID_API}/run"
headers_runpod = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {BEARER}"
}

url_backend = " https://back.connectup.cloud"
url_backend_stage = "https://stage-test.connectup.cloud"

@main.route('/')
def get_transcript():
  isAvailable = False
  if isAvailable:
    files = request.files.getlist('filename')
    transcripts = []
    for file in files:
      ROOT = os.path.join(AUDIO_FOLDER,file.filename)
      file.save(ROOT)    
      WhisperAI(ROOT)
      os.remove(ROOT)
      with open(f"{ROOT[:-4]}.json", 'r') as file_load:
        content_as_string = file_load.read()
        data = json.loads(content_as_string)
        transcripts.append(data)


    resdict = {'transcripts':transcripts}
    res = json.dumps(resdict)
  else:
    resdict = {'transcripts':[]}
    res = json.dumps(resdict)
  return res

@main.route('/savetos3', methods=['POST'])
def save_to_S3():
  files = request.files.getlist('filename')
  userId = request.form.get('user_id')
  
  for file in files:
    unique_id = str(uuid.uuid4())+".mp3"
    metadata_dict = {
        'user_id': userId,
        'original_name': file.filename,
        'state': 'for_processing'
    }
    s3_client.upload_fileobj(file, S3_BUCKET, unique_id, ExtraArgs={
            'Metadata': metadata_dict
        })
    
  
  data = {'msg':"Files uploaded successfully"}
  res = jsonify(data), 200
  return res

@main.route('/savefile', methods=['POST'])
def save_file_to_S3():
  time_init = time.time()
  auth_header = request.headers.get('Authorization')
  if not auth_header:
    return jsonify({'msg': 'Missing Authorization Header'}), 401
  token = auth_header.split(" ")[1]
  headers_request = {'Authorization': f'Bearer {token}'}
  response = requests.get(f"{url_backend}/auth", headers=headers_request)
  if response.status_code != 200:
    return jsonify({'msg': 'Invalid Token'}), 401
  print("Auth --- %s seconds ---" % (time.time() - time_init))
  #file = request.files['filename']
  time_req = time.time()
  files = request.files.getlist('filename')
  print("Request getlist --- %s seconds ---" % (time.time() - time_req))
  time_if = time.time() 
  if len(files) == 0:
    return jsonify({'msg': 'No files uploaded'}), 400
  print("If --- %s seconds ---" % (time.time() - time_if))
  
  time_decode = time.time()
  decoded_token = jwt.decode(token, BACKEND_SECRET_KEY, algorithms=["HS256"])   
  print("Decode --- %s seconds ---" % (time.time() - time_decode))

  time_user = time.time()
  userId = decoded_token['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier']
  print("User --- %s seconds ---" % (time.time() - time_user))
  print("Files --- %s seconds ---" % (time.time() - time_init))

  unique_id = f"uploads/{str(uuid.uuid4())}"

  for file in files:
    start_time = time.time()
    headers_request_test = {'Authorization': f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1laWRlbnRpZmllciI6IjhiMzY1ZTAxLTgxNzctNDEyMC1hZDEwLWQ0MTFhZTJiOTU4OSIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWUiOiJhbmRyZXMuZmFjdW5kb0Bjb25uZWN0dXB3ZWIuY29tIiwianRpIjoiMTgxYzI1MGUtYzE0Ni00OTg5LTgyNDItYTEwYzEyYTQ3NGVhIiwiUm9sZSI6IntcIklkXCI6XCI3Y2YyYzFiMi02ODkzLTRiZTUtYjQyMy0yODUwNzJhZTYzNjdcIixcIk5hbWVcIjpcIlN5c3RlbUFkbWluXCIsXCJEZXNjcmlwdGlvblwiOm51bGwsXCJwZXJtaXNzaW9uc1wiOm51bGwsXCJDb21wYW55SWRcIjowLFwiVXNlcnNDb3VudFwiOjB9IiwiZXhwIjoxNzAxOTYwMTU3fQ.c85risq7WTdLQCl3zk9c5sODFeQpA_4YROoU57AIddQ'}
    res_validation = requests.post(f"{url_backend_stage}/Transcript/ValidateExistingTranscript", json={"Transcripts":[{"Name": file.filename}]}, headers=headers_request_test)
    print(res_validation.json())
    if res_validation.status_code == 200 and res_validation.json().get('data'):
     return jsonify({'msg': 'Transcript already exists'}), 400
    elif res_validation.status_code != 200:
      return jsonify({'msg': 'Error in ValidateExistingTranscript'}), 500
    folder_s3 = f"{unique_id}/{file.filename}"
    metadata_dict = {
        'user_id': userId,
        'original_name': file.filename,
        'state': 'for_processing'
    }
    try:
      s3_client.upload_fileobj(file, "gemma-middle-storage", folder_s3, ExtraArgs={
            'Metadata': metadata_dict
        })
    except Exception as e:
      print(e)
      return jsonify({'msg': 'Error uploading file'}), 500
    print("Uploading to S3--- %s seconds ---" % (time.time() - start_time))
  print("Files uploaded--- %s seconds ---" % (time.time() - time_init))
  time_runpod = time.time() 
  data_runpod = {
      "input": {
          "folder": unique_id,
          "token_user": token
      }
  }
  response = requests.post(url_runpod, json=data_runpod, headers=headers_runpod)

  if response.status_code == 200:
      print("Respuesta exitosa:", response.json())
  else:
      print("Error en la solicitud:", response.status_code, response.text)
      return jsonify({'msg': 'Error in Runpod'}), 500
  print("Runpod --- %s seconds ---" % (time.time() - time_runpod))
  data = {'msg':"Files uploaded successfully"}
  res = jsonify(data), 200
  print("All process --- %s seconds ---" % (time.time() - time_init))
  print("--------------------")
  return res
