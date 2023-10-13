from flask import Blueprint, request, jsonify
from src.utils.WhisperAI import WhisperAI
import os
import boto3
import json
import uuid
from dotenv import load_dotenv

load_dotenv()

main = Blueprint('transcript_blueprint', __name__)

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
  file = request.files['filename']
  userId = request.form.get('user_id')
  
  unique_id = str(uuid.uuid4())+".mp3"
  metadata_dict = {
      'user_id': userId,
      'original_name': file.filename,
      'state': 'for_processing'
  }
  s3_client.upload_fileobj(file, "gemma-middle-storage", unique_id, ExtraArgs={
          'Metadata': metadata_dict
      })
  
  data = {'msg':"Files uploaded successfully", 'status':'Carlos te amo'}
  res = jsonify(data), 200
  return res
