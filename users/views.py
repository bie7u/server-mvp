from django.contrib.auth import login, logout
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.serializers import LoginSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate user and create session with HTTP-only cookie.
    
    POST /users/login
    {
        "email": "user@example.com",
        "password": "password"
    }
    
    Returns:
    {
        "user": {
            "id": 1,
            "username": "user",
            "email": "user@example.com",
            "role": "root_admin",
            "clientId": null,
            "clientName": null
        }
    }
    """
    serializer = LoginSerializer(data=request.data)
    
    try:
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # Create session and set HTTP-only cookie
        login(request, user)
        
        # Serialize user data
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)
    
    except DjangoValidationError:
        # Authentication failure (invalid credentials or inactive account)
        return Response({
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Check if this is an authentication error from the serializer
        if hasattr(serializer, 'errors') and serializer.errors:
            # Check for non-field errors which typically contain auth failures
            non_field_errors = serializer.errors.get('non_field_errors', [])
            if non_field_errors:
                return Response({
                    'message': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
            # Other validation errors (missing fields, etc.)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Re-raise unexpected errors
        raise


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user and clear session cookie.
    
    POST /users/logout
    
    Returns:
    {
        "message": "Logged out successfully"
    }
    """
    logout(request)
    return Response({
        'message': 'Logged out successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Get current authenticated user information.
    
    GET /users/me
    
    Returns:
    {
        "user": {
            "id": 1,
            "username": "user",
            "email": "user@example.com",
            "role": "root_admin",
            "clientId": null,
            "clientName": null
        }
    }
    """
    serializer = UserSerializer(request.user)
    return Response({
        'user': serializer.data
    }, status=status.HTTP_200_OK)
