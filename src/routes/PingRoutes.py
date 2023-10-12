from flask import Blueprint, jsonify

main = Blueprint('ping_blueprint', __name__)

@main.route('/')
def ping():
  return jsonify({'message': 'pong!'})