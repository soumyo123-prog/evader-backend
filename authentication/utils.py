import os
import firebase_admin
from firebase_admin import auth, credentials
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_400_BAD_REQUEST
from rest_framework.exceptions import ValidationError
from dotenv import load_dotenv

load_dotenv()

serviceAccountKey = {
    "type": os.environ.get('TYPE'),
    "project_id": os.environ.get('PROJECT_ID'),
    "private_key_id": os.environ.get('PRIVATE_KEY_ID'),
    "private_key": os.environ.get('PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": os.environ.get('CLIENT_EMAIL'),
    "client_id": os.environ.get('CLIENT_ID'),
    "auth_uri": os.environ.get('AUTH_URI'),
    "token_uri": os.environ.get('TOKEN_URI'),
    "auth_provider_x509_cert_url": os.environ.get('AUTH_PROVIDER_X509_CERT_URL'),
    "client_x509_cert_url": os.environ.get('CLIENT_X509_CERT_URL'),
}

cred = credentials.Certificate(serviceAccountKey)
firebase_admin.initialize_app(cred)


class FirebaseAPI:
    @classmethod
    def verify_id_token(cls, id_token):
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except:
            raise ValidationError(
                'Invalid Firebase ID Token.', HTTP_422_UNPROCESSABLE_ENTITY)

    @classmethod
    def get_email(cls, jwt):
        email = jwt.get('email', '')
        return email

    @classmethod
    def get_name(cls, jwt):
        name = jwt.get('name', '')
        return name

    @classmethod
    def delete_user_by_uid(cls, uid):
        auth.delete_user(uid)
