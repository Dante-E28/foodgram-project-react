from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (MAX_INGREDIENT_NAME_LENGTH,
                               MAX_MEASUREMENT_UNIT_LENGTH,
                               MAX_RECIPE_NAME_LENGTH, MAX_TAG_COLOR_LENGTH,
                               MAX_TAG_NAME_LENGTH, MIN_COOKING_TIME)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=MAX_INGREDIENT_NAME_LENGTH
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=MAX_MEASUREMENT_UNIT_LENGTH
    )

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        'Название тэга',
        max_length=MAX_TAG_NAME_LENGTH,
        unique=True
    )
    color = models.CharField(
        'Цвет',
        max_length=MAX_TAG_COLOR_LENGTH,
        unique=True
    )
    slug = models.SlugField(max_length=MAX_TAG_NAME_LENGTH, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=MAX_RECIPE_NAME_LENGTH
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    text = models.TextField(
        'Текст рецепта',
        help_text='О чем ваш рецепт?'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время готовки",
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.author}: {self.name}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.recipe} - {self.ingredient} - {self.amount}'


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='В избраном'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorites'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь списка покупок'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепты в списке покупок'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'
