from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.models import User
from users.serializers import LoginSerializer
from administration.serializers import UserReadSerializer
from myproject.settings import AUTH_COOKIE_SECURE, AUTH_COOKIE_SAMESITE, AUTH_COOKIE_HTTP_ONLY


class LoginView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            response = Response(data=UserReadSerializer(user).data, status=status.HTTP_200_OK)
            response.set_cookie(key='access', value=access, httponly=AUTH_COOKIE_HTTP_ONLY,
                                samesite=AUTH_COOKIE_SAMESITE, secure=AUTH_COOKIE_SECURE)
            response.set_cookie(key='refresh', value=refresh, httponly=AUTH_COOKIE_HTTP_ONLY,
                                samesite=AUTH_COOKIE_SAMESITE, secure=AUTH_COOKIE_SECURE)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Credentials are not provided'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            refresh = RefreshToken(refresh_token)
            refresh.verify()
            refresh.blacklist()
            user = User.objects.get(id=refresh.get('user_id'))
            new_refresh_token = RefreshToken.for_user(user)
            access = new_refresh_token.access_token
            response = Response(status=status.HTTP_200_OK)
            response.set_cookie(key='access', value=access, httponly=AUTH_COOKIE_HTTP_ONLY,
                                samesite=AUTH_COOKIE_SAMESITE, secure=AUTH_COOKIE_SECURE)
            response.set_cookie(key='refresh', value=str(new_refresh_token),  httponly=AUTH_COOKIE_HTTP_ONLY,
                                samesite=AUTH_COOKIE_SAMESITE, secure=AUTH_COOKIE_SECURE)
            return response
        except TokenError:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh')
        refresh = RefreshToken(refresh_token)
        refresh.verify()
        refresh.blacklist()
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(key='access')
        response.delete_cookie(key='refresh')
        return response


class MeView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user = self.request.user
        serializer = UserReadSerializer(user)
        return Response(serializer.data)




