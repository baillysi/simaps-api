from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request
from firebase_admin import auth


def get_rate_limit_key():
    try:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split("Bearer ")[1]
            decoded_token = auth.verify_id_token(token)
            return decoded_token.get("uid", get_remote_address())
    except Exception:
        pass
    return get_remote_address()


# Initialisation du limiter
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=["200 per day", "50 per hour"],  # limites par défaut
)
