from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import mixins
from djoser.serializers import SetPasswordSerializer

from recipes.models import Follow
from users.models import User
from users.serializers import UserSerializer, FollowSerializer, CreateUserSerializer
from api.permissions import IsCurrentUserOrAdminOrReadOnly


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (IsCurrentUserOrAdminOrReadOnly, )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return CreateUserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        if not self.request.user.is_anonymous:
            user = self.request.user
            serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response('Пользователь не авторизован', status=status.HTTP_401_UNAUTHORIZED)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        """Кастомное изменение пароля с помощью cериалайзера из пакета djoser SetPasswordSerializer."""
        serializer = SetPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data["new_password"])
            self.request.user.save()
            return Response('Пароль успешно изменен', status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, **kwargs):
        """Создание и удаление подписки ."""
        author = User.objects.get(id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            serializer = FollowSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                content = {'Подписка успешно создана': serializer.data}
                return Response(content, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if Follow.objects.filter(author=author, user=user).exists():
                Follow.objects.get(author=author).delete()
                return Response('Успешная отписка', status=status.HTTP_204_NO_CONTENT)
            return Response('Объект не найден', status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """Отображает все подписки пользователя."""
        if not self.request.user.is_anonymous:
            follows = Follow.objects.filter(user=self.request.user)
            pages = self.paginate_queryset(follows)
            serializer = FollowSerializer(pages, many=True)
            return self.get_paginated_response(serializer.data)
        return Response('Пользователь не авторизован', status=status.HTTP_401_UNAUTHORIZED)
