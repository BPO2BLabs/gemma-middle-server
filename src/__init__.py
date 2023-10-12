from flask import Flask

# Routes
from .routes import TranscriptRoutes
from .routes import PingRoutes

app = Flask(__name__)


def init_app(config):
    # Configuration
    app.config.from_object(config)

    # Blueprints
    app.register_blueprint(TranscriptRoutes.main, url_prefix='/transcripts')
    app.register_blueprint(PingRoutes.main, url_prefix='/ping')

    return app