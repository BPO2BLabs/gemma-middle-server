from flask import Blueprint, request, jsonify
import os
import requests
from dotenv import load_dotenv
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64

load_dotenv()

main = Blueprint('login_blueprint', __name__)

GEMMA_USER = os.getenv('GEMMA_USER')
GEMMA_PASS = os.getenv('GEMMA_PASS')
URL_BACKEND = os.getenv('URL_BACKEND')
PEM_PATH = os.getenv('PEM_PATH')
RUNPOD_PASS = os.getenv('RUNPOD_PASS')

public_key = RSA.importKey(open(PEM_PATH).read())
cipher = PKCS1_OAEP.new(public_key)


@main.route('/toorchestrator', methods=['POST'])
def to_orchestrator():
    print(request.json)
    secret_password = request.json['secret_password']
    if secret_password != RUNPOD_PASS:
        return jsonify({"message": "Unauthorized"}), 401        
    encrypted_pass = cipher.encrypt(GEMMA_PASS.encode('utf-8'))
    encrypted_pass_b64 = base64.b64encode(encrypted_pass).decode('utf-8')
    form_data ={
    "userName": GEMMA_USER,
    "password": encrypted_pass_b64
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{URL_BACKEND}/auth", json=form_data, headers=headers)
    return jsonify(response.json()), response.status_code