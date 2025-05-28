import json
from flask import Flask
from flask_cors import CORS
from firebase_admin import initialize_app, credentials
from google.cloud import secretmanager
from app.controllers.hike_controller import hike_bp
from app.controllers.review_controller import review_bp
from app.controllers.viewpoint_controller import viewpoint_bp
from app.controllers.data_controller import zone_bp, region_bp, journey_bp
from app.config import config, env
from app.auth import add_custom_claims
from app.limiter import limiter
from app.logger import logger


def create_app():
    logger.info(F"Initialisation de l'app Flask <> ENV : {env}")
    app = Flask(__name__)

    # CORS
    CORS(app, supports_credentials=True) if env == "dev" else CORS(app, resources={
            r"/api/*": {"origins": "https://kavaleapp.com"}
        }, supports_credentials=True)

    # Rate Limiter
    limiter.init_app(app)

    # Initialisation de Firebase
    firebase_app = _init_firebase()

    # Optionnel : on stocke l'instance dans la config si on veut y accéder ailleurs
    app.config["FIREBASE_APP"] = firebase_app

    # Blueprints
    app.register_blueprint(hike_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(viewpoint_bp)
    app.register_blueprint(zone_bp)
    app.register_blueprint(region_bp)
    app.register_blueprint(journey_bp)

    return app


def _init_firebase():
    if env == "dev":
        return initialize_app()
    else:
        client = secretmanager.SecretManagerServiceClient()
        name = client.secret_version_path(
            config["project_id"],
            config["firebase_sdk_admin_secret_id"],
            config["firebase_sdk_admin_version_id"]
        )
        response = client.access_secret_version(request={"name": name})
        payload = json.loads(response.payload.data.decode("UTF-8"))
        creds = credentials.Certificate(payload)
        return initialize_app(credential=creds)
