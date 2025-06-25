import secrets
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from users.models import UserToken

User = get_user_model()


class SimpleTokenAuthentication(BaseAuthentication):
    """
    Simple token authentication for the medical app
    """
    
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        
        if not token:
            return None
            
        # Remove 'Token ' prefix if present
        if token.startswith('Token '):
            token = token[6:]
            
        try:
            user_token = UserToken.objects.get(token=token, is_active=True)
            return (user_token.user, token)
        except UserToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token')


def generate_token():
    """
    Generate a simple token for user authentication
    """
    return secrets.token_urlsafe(32)


def create_user_token(user):
    """
    Create a new token for a user
    """
    # Deactivate any existing tokens for this user
    UserToken.objects.filter(user=user, is_active=True).update(is_active=False)
    
    # Create new token
    token = generate_token()
    user_token = UserToken.objects.create(user=user, token=token)
    return user_token 