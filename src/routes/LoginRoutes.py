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
    form_data ={
    "userName": "daniel.gomez@bpo2b.com",
    "password": "UNbDEa/Aacz/Csj7NJyfMu2DL2GZHWXVUFHzIMUy1h+H+X4y5aNv9Mh4RHQ9EhJ8HstT6Z52Zox5/dV4x4uK88K6MItfdnEOd8P8oHer2mSaelG7k0Y87t365WKZx0QwM5NJJ2OBK0hJCipe6KpFw4YJiAnKVsE90KPmdGbUDQCZWPHlzYmzdc6daqUUGiI/ohQuqw7q5orffVgo+3c8vK7t0rMm/HMizpK8Gr/9zWPKcS8+Rz4t21si/+e0VFVWbNn1iJ7v7F3G+wHVLhafLjcTpm9uQfNrv1YdnIdJF9jLnYPilKhGi+gVn+Xot5q2yEAYDHxPw0Ei0ytE2YhgCA=="
    }
    print(form_data)
    headers = {
                "Content-Type": "application/json",
                "Accept-Enconding": "gzip, deflate, br",
                "Accept": "*/*",
                "Connection": "keep-alive"}
    response = requests.post(f"{URL_BACKEND}/auth", data=form_data, headers=headers)
    print(response.json())
    return jsonify(response.json())
    
