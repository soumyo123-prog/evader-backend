from django.db import models
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .utils import FirebaseAPI


class LoginSerializer(serializers.Serializer):
    id_token = serializers.CharField(max_length=2400)

    def validate_access_token(self, access_token):
        return FirebaseAPI.verify_id_token(access_token)

    def validate(self, data):
        User = get_user_model()
        id_token = data.get('id_token', None)
        current_user = None
        jwt = self.validate_access_token(id_token)
        uid = jwt['uid']

        if User.objects.filter(uid=uid).exists():
            current_user = User.objects.filter(uid=uid)[0]
        else:
            email = FirebaseAPI.get_email(jwt)
            name = FirebaseAPI.get_name(jwt)
            # We keep username=uid untill user explicitly provides it from frontend.
            current_user = User.objects.create(
                uid=uid, name=name, email=email, username=uid)

        data['user'] = current_user
        return data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('uid', 'name', 'email',)
