from rest_framework import serializers
from api.models import UserMaster
from django.contrib.auth.hashers import make_password
from socialnetwork.tokens import get_access_token, get_refresh_token

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, max_length=25)
    confirm_password = serializers.CharField(required=True, max_length=25)
    name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = UserMaster
        fields = ["name", 'email', 'password', "confirm_password"]

    def validate(self, attrs):
        password = attrs.get("password", None)
        confirm_password = attrs.get("confirm_password", None)
        if password != confirm_password:
            raise serializers.ValidationError({'error': "Passwords didn't match"})
        return attrs

    def create(self, validated_data):
        name = validated_data.get('name')
        email = validated_data.get('email').lower()  # Convert email to lowercase
        password = validated_data.get('password')
        hashed_password = make_password(password)
        UserMaster.objects.create(name=name, email=email, password=hashed_password)
        return validated_data


class UserLoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, max_length=25)
    email = serializers.CharField(required=True)

    class Meta:
        model = UserMaster
        fields = ['email', "password"]

    def validate(self, attrs):
        email = attrs.get('email').lower()  # Convert email to lowercase
        try:
            user = UserMaster.objects.get(email=email)
        except UserMaster.DoesNotExist:
            raise serializers.ValidationError({'error': "Invalid Email"})
        
        if not user.check_password(attrs.get("password")):
            raise serializers.ValidationError({'error': "Invalid Password"})
        
        return attrs, user


class UserLoginDataSerialzier(serializers.ModelSerializer):
    access_token = serializers.SerializerMethodField()
    refresh_token = serializers.SerializerMethodField()

    class Meta:
        model = UserMaster
        fields = ['id', 'name', 'email', 'access_token', "refresh_token"]

    def get_access_token(self, obj):
        access_token = get_access_token(obj)
        return access_token

    def get_refresh_token(self, obj):
        refresh_token = get_refresh_token(obj)
        return refresh_token


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMaster
        fields = ['id', 'name', 'email']
