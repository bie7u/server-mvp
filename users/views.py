from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import authenticate
from django.conf import settings
from users.models import ClientUserM


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate user and set JWT tokens in HTTP-only cookies.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "password"
    }
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'message': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate using email (Django uses username by default)
    # We need to get the user by email first
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'message': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check password
    if not user.check_password(password):
        return Response(
            {'message': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check if user is active
    if not user.is_active:
        return Response(
            {'message': 'User account is disabled'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    # Prepare user data
    user_data = {
        'id': user.id,
        'name': user.get_full_name() or user.username,
        'email': user.email,
    }
    
    # Get role from ClientUserM if exists
    try:
        client_user = ClientUserM.objects.get(user=user)
        user_data['role'] = client_user.role
        user_data['clientId'] = client_user.client.id if client_user.client else None
        user_data['clientName'] = client_user.client.name if client_user.client else None
    except ClientUserM.DoesNotExist:
        # Check if superuser/staff for root_admin role
        if user.is_superuser or user.is_staff:
            user_data['role'] = 'root_admin'
        else:
            user_data['role'] = 'client_user'
        user_data['clientId'] = None
        user_data['clientName'] = None
    
    # Create response
    response = Response({
        'message': 'Login successful',
        'user': user_data
    }, status=status.HTTP_200_OK)
    
    # Set HTTP-only cookies
    response.set_cookie(
        key=settings.AUTH_COOKIE,
        value=access_token,
        max_age=settings.AUTH_COOKIE_MAX_AGE,
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path=settings.AUTH_COOKIE_PATH,
    )
    
    response.set_cookie(
        key=settings.AUTH_COOKIE_REFRESH,
        value=refresh_token,
        max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path=settings.AUTH_COOKIE_PATH,
    )
    
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh the access token using the refresh token from HTTP-only cookie.
    """
    refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
    
    if not refresh_token:
        return Response(
            {'message': 'Refresh token not found'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        # Create response
        response = Response({
            'message': 'Token refreshed successfully'
        }, status=status.HTTP_200_OK)
        
        # Set new access token cookie
        response.set_cookie(
            key=settings.AUTH_COOKIE,
            value=access_token,
            max_age=settings.AUTH_COOKIE_MAX_AGE,
            secure=settings.AUTH_COOKIE_SECURE,
            httponly=settings.AUTH_COOKIE_HTTP_ONLY,
            samesite=settings.AUTH_COOKIE_SAMESITE,
            path=settings.AUTH_COOKIE_PATH,
        )
        
        # If ROTATE_REFRESH_TOKENS is True, also set new refresh token
        if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
            new_refresh_token = str(refresh)
            response.set_cookie(
                key=settings.AUTH_COOKIE_REFRESH,
                value=new_refresh_token,
                max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE,
                path=settings.AUTH_COOKIE_PATH,
            )
        
        return response
        
    except (TokenError, InvalidToken) as e:
        return Response(
            {'message': 'Invalid or expired refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user by clearing JWT cookies.
    """
    response = Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)
    
    # Delete cookies
    response.delete_cookie(
        key=settings.AUTH_COOKIE,
        path=settings.AUTH_COOKIE_PATH,
    )
    
    response.delete_cookie(
        key=settings.AUTH_COOKIE_REFRESH,
        path=settings.AUTH_COOKIE_PATH,
    )
    
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Get current user information.
    """
    user = request.user
    user_data = {
        'id': user.id,
        'name': user.get_full_name() or user.username,
        'email': user.email,
    }
    
    # Get role from ClientUserM if exists
    try:
        client_user = ClientUserM.objects.get(user=user)
        user_data['role'] = client_user.role
        user_data['clientId'] = client_user.client.id if client_user.client else None
        user_data['clientName'] = client_user.client.name if client_user.client else None
    except ClientUserM.DoesNotExist:
        # Check if superuser/staff for root_admin role
        if user.is_superuser or user.is_staff:
            user_data['role'] = 'root_admin'
        else:
            user_data['role'] = 'client_user'
        user_data['clientId'] = None
        user_data['clientName'] = None
    
    return Response({
        'user': user_data
    }, status=status.HTTP_200_OK)

