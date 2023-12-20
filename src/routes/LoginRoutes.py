from flask import Blueprint, request, jsonify
import os
import requests
from dotenv import load_dotenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

load_dotenv()

main = Blueprint('login_blueprint', __name__)

GEMMA_USER = os.getenv('GEMMA_USER')
GEMMA_PASS = os.getenv('GEMMA_PASS')
URL_BACKEND = os.getenv('URL_BACKEND')
PEM_PATH = os.getenv('PEM_PATH')

with open(PEM_PATH, "rb") as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )

@main.route('/toorchestrator', methods=['GET'])
def to_orchestrator():
    encrypted_pass = public_key.encrypt(
        GEMMA_PASS.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ),
    )
    form_data = {"username":GEMMA_USER,"password":encrypted_pass}
    response = requests.post(f"{URL_BACKEND}/auth", json=form_data)
    print(response)
    return jsonify(response.json())
    
