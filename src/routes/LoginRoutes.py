from flask import Blueprint, request, jsonify
import os
import requests
from dotenv import load_dotenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import base64

load_dotenv()

main = Blueprint('login_blueprint', __name__)

GEMMA_USER = os.getenv('GEMMA_USER')
GEMMA_PASS = os.getenv('GEMMA_PASS')
URL_BACKEND = os.getenv('URL_BACKEND')
MODULUS_B64_PUBLIC_KEY = os.getenv('MODULUS_B64_PUBLIC_KEY')
EXPONENT_B64_PUBLIC_KEY = os.getenv('EXPONENT_B64_PUBLIC_KEY')

modulus = int.from_bytes(base64.b64decode(MODULUS_B64_PUBLIC_KEY), byteorder='big')
exponent = int.from_bytes(base64.b64decode(EXPONENT_B64_PUBLIC_KEY), byteorder='big')

public_numbers = rsa.RSAPublicNumbers(exponent, modulus)
public_key = public_numbers.public_key(backend=default_backend())



@main.route('/toorchestrator', methods=['GET'])
def to_orchestrator():
    encrypted_pass = public_key.encrypt(
        GEMMA_PASS.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ),
    )
    encrypted_pass_b64 = base64.b64encode(encrypted_pass).decode('utf-8')
    form_data = {"userName":GEMMA_USER,"password":encrypted_pass_b64}
    print(form_data)
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{URL_BACKEND}/auth", data=form_data, headers=headers)
    print(response)
    return jsonify(response.json())
    
