from flask import Flask
from flask_cors import CORS

# Routes
from .routes import TranscriptRoutes
from .routes import PingRoutes
from .routes import LoginRoutes

app = Flask(__name__)
CORS(app)


def init_app(config):
    # Configuration
    app.config.from_object(config)

    # Blueprints
    app.register_blueprint(TranscriptRoutes.main, url_prefix='/transcripts')
    app.register_blueprint(PingRoutes.main, url_prefix='/ping')
    app.register_blueprint(LoginRoutes.main, url_prefix='/login')
    
    return app