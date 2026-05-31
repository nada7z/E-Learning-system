from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Student, Teacher
from django.utils import timezone
from rest_framework_simplejwt.exceptions import AuthenticationFailed

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['bio', 'profile_picture', 'date_of_birth']


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['specialization', 'experience_years', 'biography']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data['role'],
            password=validated_data['password']
        )

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        now = timezone.now()

        if user.account_status == "banned":
            raise AuthenticationFailed("Your account is banned.")

        if user.account_status == "suspended":
            if user.suspended_until and user.suspended_until > now:
                raise AuthenticationFailed(
                    f"Your account is suspended until {user.suspended_until.strftime('%Y-%m-%d')}."
                )

            user.account_status = "normal"
            user.suspended_until = None
            user.save(update_fields=["account_status", "suspended_until"])

        data["user"] = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }

        return data