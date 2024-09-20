import datetime
import jwt
import uuid
from django.conf import settings


def get_access_token(user):
    payload = {
        'user_id': user.id,
        "name":user.name,
        'token_type': 'access',
        'exp': datetime.datetime.now() + datetime.timedelta(minutes=15),
        'jti': str(uuid.uuid4()).replace("-","")}
    access_token = jwt.encode(payload,settings.SECRET_KEY, algorithm='HS256')
    return access_token



def get_refresh_token(user):
    payload = {
        'user_id': user.id,
        "name":user.name,
        'token_type': 'refresh',
        'exp': datetime.datetime.now() + datetime.timedelta(days=7),
        'jti': str(uuid.uuid4()).replace("-","")}
    refresh_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return refresh_token