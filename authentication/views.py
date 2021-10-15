from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import LoginSerializer, ProfileSerializer

User = get_user_model()

# Create your views here.


def create_auth_token(user):
    token, created = Token.objects.get_or_create(user=user)
    return token.key


class LoginView(GenericAPIView):
    authentication_classes = []
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        token = create_auth_token(user)

        return Response(data={'token': token}, status=status.HTTP_200_OK)


class ProfileView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        user = serializer.data
        return Response(data={'user': user}, status=status.HTTP_200_OK)
