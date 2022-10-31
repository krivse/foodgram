from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Recipe, Ingredient, Tag, IngredientRecipe, ShoppingCart, Favorite
from users.serializers import UserSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер модели Favorite."""
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    coocking_time = serializers.IntegerField(source='recipe.cooking_time', read_only=True)
    id = serializers.PrimaryKeyRelatedField(source='recipe', queryset=Recipe.objects)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'coocking_time')

    #def validate(self, data):
    #    if Favorite.objects.filter(author=data['author'], recipe=data['recipe']).exists():
    #        raise serializers.ValidationError("Рецепт уже добавлен в избранное.")
    #    return data


    #def create(self, validated_data):
    #    return Favorite.objects.create(**validated_data)

        #extra_kwargs = {
            #'recipe': {'source': 'id', 'read_only': True},
            #'id': {'write_only': True}}
        #validators = [
        #    UniqueTogetherValidator(
         #       queryset=Favorite.objects.all(),
         #       fields=('recipe', 'author'))]
    #def create(self, validated_data):
    #    user = self.context['requests'].author
    #    print(f'fasfas{user}')
    #    self.initial_data['author'] = user
    #    print(validated_data)
    #    return Favorite.objects.create(**validated_data)
#    def get_id(self, obj):
 #       user = self.context('requests').user
  #      id = recipes.filter(author=user, recipe=obj)
   #     return FavoriteSerializer(id).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериалайзер модели Cart."""
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    coocking_time = serializers.IntegerField(source='recipe.cooking_time', read_only=True)
    id = serializers.PrimaryKeyRelatedField(source='recipe', queryset=Recipe.objects)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'coocking_time')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = '__all__',


class TagSerializer(serializers.ModelSerializer):
    """Serializer для модели Tag."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = '__all__',


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Serializer для связаной модели Recipe и Ingredient."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Serializer для модели Recipe - чтение данных.
    Находится ли рецепт в избранном, списке покупок.
    Получение списка ингредиентов с добавленным полем amount из промежуточной модели.
    """
    author = UserSerializer()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(many=True, source='recipe_ingredients', read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',)

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(recipe=obj).exists()


class AddIngredientSerializer(serializers.ModelSerializer):
    """
    Serializer для поля ingredient модели Recipe - создание ингредиентов.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Serializer для модели Recipe - запись / обновление / удаление данных."""
    ingredients = AddIngredientSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')

    def to_representation(self, instance):
        ingredients = super().to_representation(instance)
        ingredients['ingredients'] = IngredientRecipeSerializer(instance.recipe_ingredients.all(), many=True).data
        return ingredients

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=ingredient['id'], amount=ingredient['amount'])
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=instance, ingredient=ingredient['id'], amount=ingredient['amount'])
        instance.tags.set(tags)
        return super().update(instance, validated_data)


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Сериализатор предназначен для вывода рецептом в FollowSerializer."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)
