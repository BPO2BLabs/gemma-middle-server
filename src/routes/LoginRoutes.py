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

public_key = RSA.importKey(open(PEM_PATH).read())
cipher = PKCS1_OAEP.new(public_key)


@main.route('/toorchestrator', methods=['GET'])
def to_orchestrator():
    encrypted_pass = cipher.encrypt(GEMMA_PASS.encode('utf-8'))
    print("enc_pass",encrypted_pass)
    encrypted_pass_b64 = base64.b64encode(encrypted_pass).decode('utf-8')
    form_data = {"userName":GEMMA_USER,"password":encrypted_pass_b64}
    print(form_data)
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{URL_BACKEND}/auth", data=form_data, headers=headers)
    print(response)
    return jsonify(response.json())
    
