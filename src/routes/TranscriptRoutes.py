from flask import Blueprint, request, jsonify
from src.utils.WhisperAI import WhisperAI
import os
import boto3
import json
import uuid
from dotenv import load_dotenv
import requests
import jwt

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
  auth_header = request.headers.get('Authorization')
  if not auth_header:
    return jsonify({'msg': 'Missing Authorization Header'}), 401
  token = auth_header.split(" ")[1]
  headers_request = {'Authorization': f'Bearer {token}'}
  response = requests.get(f"{url_backend}/auth", headers=headers_request)
  if response.status_code != 200:
    return jsonify({'msg': 'Invalid Token'}), 401

  #file = request.files['filename']
  files = request.files.getlist('filename')
  decoded_token = jwt.decode(token, BACKEND_SECRET_KEY, algorithms=["HS256"])   
  userId = decoded_token['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier']
  
  unique_id = str(uuid.uuid4())
  for file in files:
    unique_id_name = str(uuid.uuid4())
    folder_s3 = f"{unique_id}/{unique_id_name}.mp3"
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
  data = {'msg':"Files uploaded successfully"}
  res = jsonify(data), 200
  return res
