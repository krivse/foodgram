from django.db import models
from django.core.validators import MinValueValidator
from users.models import User
from django.db.models import Q, F


class Ingredient(models.Model):
    """Ингридиенты для рецептов."""
    name = models.CharField(
        verbose_name='Название ингридиента',
        max_length=200, db_index=True,
        help_text='Введите название ингридиента')
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        help_text='Введите единицу измерения')

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Тэги для рецептов с предустановленным выбором."""
    GREEN = '09db4f'
    ORANGE = 'fa6a02'
    PURPLE = 'b813d1'
    COLOR_TAG = [
        (GREEN, 'Зеленый'),
        (ORANGE, 'Оранжевый'),
        (PURPLE, 'Фиолетовый')
    ]
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200, unique=True,
        help_text='Введите название тега')
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=7, unique=True,
        default=GREEN,
        choices=COLOR_TAG,
        help_text='Выберите цвет')
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=200, unique=True,
        help_text='Укажите уникальный слаг')

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель для рецептов.
    У автора не может быть создано более одного рецепта с одним именем.
    """
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        help_text='Автор рецепта')
    ingredient = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингридиент')
    tag = models.ManyToManyField(
        Tag,
        verbose_name='Название тега',
        help_text='Выберите tag')
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Опишите приготовление рецепта')
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
        help_text='Введите название рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1, 'Минимальное время приготовления')],
        help_text='Укажите время приготовления рецепта в минутах')
    image = models.ImageField(
        verbose_name='Картинка рецепта',
        upload_to='media/',
        help_text='Добавьте изображение рецепта')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        default_related_name = 'recipe'
        verbose_name = "Рецепт"
        verbose_name_plural = 'Рецепты'
        constraints = [models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe')]

    def __str__(self):
        return f'{self.name}'


class IngredientRecipe(models.Model):
    """
    Ингридиенты для рецепта.
    Промежуточная модель между таблиц:
      Recipe и Ingredient
    """
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Название рецепта',
        on_delete=models.CASCADE,
        help_text='Выберите рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингридиент',
        on_delete=models.CASCADE,
        help_text='Укажите ингридиенты')
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, 'Минимальное количество ингридиентов 1')],
        verbose_name='Количество',
        help_text='Укажите количество ингридиента')

    class Meta:
        default_related_name = 'ingredient_recipe'
        verbose_name = "Cостав рецепта"
        verbose_name_plural = "Состав рецепта"
        constraints = [models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients')]


class Cart(models.Model):
    """
    Список покупок пользователя.
    Ограничения уникальности полей:
      author, recipe.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт для приготовления',
        on_delete=models.CASCADE,
        help_text='Выберите рецепт для приготовления')

    class Meta:
        default_related_name = 'cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [models.UniqueConstraint(
            fields=['author', 'recipe'],
            name='unique_cart')]


class Favorite(models.Model):
    """
    Список покупок пользователя.
    Ограничения уникальности полей:
      author, recipe.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты')

    class Meta:
        default_related_name = 'favorite'
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [models.UniqueConstraint(
            fields=['author', 'recipe'],
            name='unique_favorite')]


class Follow(models.Model):
    """
    Подписки на авторов рецептов.
    Ограничения уникальности полей:
      author, user.
    """
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
        help_text='Подписчик автора рецепта')
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецептов',
        related_name='followed',
        on_delete=models.CASCADE,
        help_text='Автор рецепта')

    class Meta:
        verbose_name = 'Мои подписки'
        verbose_name_plural = 'Мои подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_following')]
