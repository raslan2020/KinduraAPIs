from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User, UserToken
from .models import UserJSON
from utils.authentication import create_user_token


class UserSignupSerializer(serializers.ModelSerializer):
    """
    Serializer for user signup
    """
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'username']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'age', 'gender', 'address', 'terms_and_conditions']
        extra_kwargs = {
            'terms_and_conditions': {'required': True}
        }
    
    def validate_terms_and_conditions(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the terms and conditions")
        return value


class UserTokenSerializer(serializers.ModelSerializer):
    """
    Serializer for user tokens
    """
    class Meta:
        model = UserToken
        fields = ['token', 'created_at']


class UserJSONUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model = UserJSON
        fields = ['id', 'uploaded_at', 'data', 'file']
        read_only_fields = ['id', 'uploaded_at', 'data']

    def create(self, validated_data):
        file = validated_data.pop('file')
        import json
        data = json.load(file)
        user = self.context['request'].user
        return UserJSON.objects.create(user=user, data=data)  # type: ignore[attr-defined] 