from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from recipes.models import Recipe, Tag, Ingredient, Favorite, ShoppingCart
from api.serializers import (
    RecipeListSerializer, TagSerializer, IngredientSerializer, FavoriteSerializer,
    ShoppingCartSerializer, RecipeWriteSerializer)
from api.services import shopping_cart
from api.permissions import IsOwnerOrAdminOrReadOnly
from users.models import User


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Функция для модели тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Функция для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe: [GET, POST, DELETE, PATCH]."""
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filterset_fields = ('tags',)
    search_fields = ('^ingredients__name',)
    ordering = ('-id',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post', 'delete', 'get'], )
    def favorite(self, request, *args, **kwargs):
        """Получить / Добавить / Удалить  рецепт из избранного у текущего пользоватля."""
        if request.method == 'GET':
            if not self.request.user.is_anonymous:
                favorite = Favorite.objects.filter(recipe=self.kwargs.get('pk'), author=request.user)
                serializer = FavoriteSerializer(favorite, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response('Пользователь не авторизован', status=status.HTTP_401_UNAUTHORIZED)
        elif request.method == 'POST':
            recipe = Recipe.objects.get(id=self.kwargs.get('pk'))
            serializer = FavoriteSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=self.request.user, recipe=recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.get(recipe=self.kwargs.get('pk')).delete()
        return Response(request.data, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='favorite')
    def favorites(self, request, *args, **kwargs):
        """Просмотп всех избранных рецептов пользователя."""
        if not self.request.user.is_anonymous:
            favorite = Favorite.objects.filter(author=request.user)
            pages = self.paginate_queryset(favorite)
            serializer = FavoriteSerializer(pages, many=True)
            return self.get_paginated_response(serializer.data)
        return Response('Пользователь не авторизован', status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['post', 'delete', 'get'])
    def shopping_cart(self, request, **kwargs):
        """Получить / Добавить / Удалить  рецепт из списка покупок у текущего пользоватля."""
        if request.method == 'GET':
            if not self.request.user.is_anonymous:
                shopping_cart = ShoppingCart.objects.filter(recipe=self.kwargs.get('pk'), author=request.user)
                serializer = ShoppingCartSerializer(shopping_cart, many=True)
                return Response(serializer.data)
            return Response('Пользователь не авторизован', status=status.HTTP_401_UNAUTHORIZED)
        elif request.method == 'POST':
            recipe = Recipe.objects.get(id=self.kwargs.get('pk'))
            serializer = ShoppingCartSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=self.request.user, recipe=recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            ShoppingCart.objects.get(recipe=self.kwargs.get('pk')).delete()
            return Response(request.data, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def download_shopping_cart(self, request):
        author = User.objects.get(id=self.request.user.pk)
        if not self.request.user.is_anonymous or self.request.user == author:
            return shopping_cart(self, request, author)
        return Response('Пользователь не авторизован', status=status.HTTP_401_UNAUTHORIZED)
