from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, User


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart')
    is_favorited = filters.NumberFilter(
        method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__author=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_cart__author=self.request.user)
        return queryset
