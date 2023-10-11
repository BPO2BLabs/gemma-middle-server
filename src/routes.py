#!/usr/bin/env python3
from flask import Flask, request, jsonify
import boto3
import os
import json
app = Flask(__name__)

# ACCESS_KEY_ID=os.environ.get('ACCESS_KEY_ID')
# ACCESS_SECRET_KEY=os.environ.get('ACCESS_SECRET_KEY')
# BUCKET_NAME=os.environ.get('BUCKET_NAME')
cwd = os.getcwd()
env_path= cwd + '/.env.json'
with open(env_path, 'r') as f:
    # Load the JSON data into a Python object
    data = json.load(f)

# Access the data in the Python object

ACCESS_KEY_ID=data['ACCESS_KEY_ID']
ACCESS_SECRET_KEY=data['ACCESS_SECRET_KEY']
BUCKET_NAME=data['BUCKET_NAME']

@app.route('/ping', methods=['GET'])
def ping():
    response_body = {
        "message": "Hello from gemma middle server "
    }
    return jsonify(response_body), 200

@app.route('/audio/list', methods=['POST'])
def getAllObjects():

    s3 = boto3.resource('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=ACCESS_SECRET_KEY)

    #get all objects in bucket
    list_of_files = [str(obj.key) for obj in s3.Bucket(BUCKET_NAME).objects.all()]
    
    print('list of files',list_of_files)

    metadata_list =[]

    for item in list_of_files:
        metadata_list.append({
            'key':item,
            'metadata': s3.Bucket(BUCKET_NAME).Object(item).metadata
            })

    response_body = {
        "list_files": metadata_list
    }
    
    return jsonify(response_body), 200

@app.route('/audio/create', methods=['POST'])
def saveObject():
    # Get the file from the POST request
    file = request.files['file']

    # Get the metadata labels from the POST request
    userName = request.form.get('user_name')
    userId = request.form.get('user_id')

    #define the metadata dictionary
    metadata_dict = {
        'user_name': userName,
        'user_id': userId,
        'state': 'for_processing'
    }

    # Create an S3 client
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=ACCESS_SECRET_KEY)
    
    # Save the file to the S3 bucket with metadata labels
    # Don't forget that validate info in metadata_dict, values must be not null
    s3.upload_fileobj(
        file,
        BUCKET_NAME,
        file.filename,
        ExtraArgs={
            'Metadata': metadata_dict
        }
    )
    object_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file.filename}"

    return jsonify({'message': 'File saved successfully', 'object': object_url }), 200

@app.route('/audio/update', methods=['PUT'])
def updateObject():
    # Get the file from the PUT request
    fileKey =  request.form.get('file_key')
    fileState= request.form.get('file_state')

    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=ACCESS_SECRET_KEY)

    metadata = s3.get_object(Bucket=BUCKET_NAME, Key=fileKey)['Metadata']


    metadata['state']= fileState

    s3.copy_object(Bucket=BUCKET_NAME, CopySource={'Bucket': BUCKET_NAME, 'Key': fileKey},
               Key=fileKey, Metadata=metadata, MetadataDirective='REPLACE')
  

    return jsonify({'message': 'File updated successfully' }), 200

@app.route('/audio/delete', methods=['DELETE'])
def deleteObject():
    # Get the file from the PUT request
    fileKey =  request.form.get('file_key')

    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=ACCESS_SECRET_KEY)

    response = s3.delete_object(
        Bucket=BUCKET_NAME,
        Key=fileKey)

    print(response)
  
    return jsonify({'message': 'File deleted successfully' }), 200
  
@app.route('/s3/events', methods=['POST'])
def s3Events():
    print('s3 events', request.json)
    return 200
    
    



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
