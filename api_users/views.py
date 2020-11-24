from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login

from drf_rw_serializers import viewsets

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import ReadOnlyUserSerializer, WriteOnlyUserSerializer


User = get_user_model()


class LoginToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        result = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=result.data['token'])
        update_last_login(None, token.user)
        return result


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    read_serializer_class = ReadOnlyUserSerializer
    write_serializer_class = WriteOnlyUserSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
