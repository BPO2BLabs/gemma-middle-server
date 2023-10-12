from flask import Blueprint, request, jsonify
from src.utils.WhisperAI import whisperAI
import os
import boto3
import json

main = Blueprint('language_blueprint', __name__)

main.config['AUDIO_FOLDER'] = os.path.join("/home","ubuntu",".tmpaud")
main.config['S3_BUCKET'] = os.getenv('BUCKET_NAME')
main.config['S3_KEY'] = os.getenv('ACCESS_KEY_ID')
main.config['S3_SECRET'] = os.getenv('ACCESS_SECRET_KEY')
session = boto3.Session(
    aws_access_key_id=main.config['S3_KEY'],
    aws_secret_access_key=main.config['S3_SECRET']
)
s3_session = session.client('s3')
s3_resource = session.resource('s3')
s3_client = boto3.client('s3', aws_access_key_id=main.config['S3_KEY'], aws_secret_access_key=main.config['S3_SECRET'])

@main.route('/')
def get_transcript():
  files = request.files.getlist('filename')
  transcripts = []
  for file in files:
    ROOT = os.path.join(main.config['AUDIO_FOLDER'],file.filename)
    file.save(ROOT)    
    whisperAI(ROOT)
    os.remove(ROOT)
    with open(f"{ROOT[:-4]}.json", 'r') as file_load:
      content_as_string = file_load.read()
      data = json.loads(content_as_string)
      transcripts.append(data)


  resdict = {'transcripts':transcripts}
  res = json.dumps(resdict)
  return res

@main.route('/savetos3')
def save_to_S3():
  files = request.files.getlist('filename')
  for file in files:
    ROOT = os.path.join(main.config['AUDIO_FOLDER'],file.filename)
    file.save(ROOT)
    s3_client.upload_file(ROOT, main.config['S3_BUCKET'], file.filename)
    os.remove(ROOT)

  data = {'msg':"Files uploaded successfully"}
  res = jsonify(data)
  return res
