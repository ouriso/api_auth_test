from django.contrib.auth import get_user_model

from rest_framework import serializers


User = get_user_model()


class ReadOnlyUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',
                  'is_active', 'last_login', 'is_superuser')


class WriteOnlyUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'password', 'is_active')
