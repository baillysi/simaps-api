import firebase_admin
from firebase_admin import auth
from flask import request
from functools import wraps
from app.logger import logger


def verify_firebase_token_and_role(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Vérifier si le token d'autorisation est présent
        if "Authorization" not in request.headers:
            logger.error("Authorization header is missing")
            return {"message": "Missing authorization token"}, 401

        authorization = request.headers["Authorization"]

        # Vérifier que l'en-tête est sous la forme "Bearer <token>"
        if not authorization.startswith("Bearer "):
            logger.error("Invalid authorization format")
            return {"message": "Invalid authorization format"}, 401

        token = authorization.split("Bearer ")[1]

        try:
            # Vérification du token Firebase
            decoded_token = auth.verify_id_token(token)
            request.user_id = decoded_token["uid"]
            logger.info(f"Token successfully verified for user {request.user_id}")
            # Vérification du rôle admin
            role = get_user_role()
            if role == 'admin':
                logger.error(f"Insufficient permissions for user {request.user_id}")
                return {"message": f"Insufficient permissions, required role: admin"}, 403
        except firebase_admin.auth.InvalidIdTokenError:
            logger.error(f"Invalid token")
            return {"message": "Invalid token"}, 401
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return {"message": f"Error verifying token: {str(e)}"}, 401

        return f(*args, **kwargs)

    return decorated_function


def get_user_role():
    return getattr(request, "user_role", "anonymous")


def get_user_id():
    return getattr(request, "user_id", None)


def add_custom_claims(user_id):
    # Ajouter un custom claim (ici, un rôle "admin")
    auth.set_custom_user_claims(user_id, {'role': 'admin'})
    logger.info(f"Custom claims for user {user_id} set successfully.")
