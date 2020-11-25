from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LoginToken, UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('api-token-auth/', LoginToken.as_view(), name='token-auth'),
    path('api/v1/', include(router.urls)),
]
