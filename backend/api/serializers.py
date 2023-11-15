from django.db.models import F
from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.models import (Favorites, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from services.validators import ingredients_validator, tags_validator
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class MiniRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FavoritesSerializer(ShoppingCartSerializer):
    class Meta:
        model = Favorites
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=True, allow_null=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientrecipe__amount'),
        )

    def get_tags(self, obj):
        return obj.tags.values(
            'id',
            'name',
            'color',
            'slug'
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')

        ingredients_validator(ingredients)
        tags_validator(tags)

        data.update(
            {
                'ingredients': ingredients,
                'tags': tags
            }
        )

        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            pk = ingredient['id']
            amount = ingredient['amount']
            ing = Ingredient.objects.get(id=pk)
            IngredientRecipe.objects.create(
                ingredient=ing,
                recipe=recipe,
                amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        if ingredients:
            instance.ingredients.clear()
            for ingredient in ingredients:
                pk = ingredient['id']
                amount = ingredient['amount']
                ing = Ingredient.objects.get(id=pk)
                IngredientRecipe.objects.create(
                    ingredient=ing,
                    recipe=instance,
                    amount=amount
                )

        if tags:
            instance.tags.clear()
            instance.tags.set(tags)

        return super().update(instance, validated_data)
