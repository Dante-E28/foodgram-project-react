from django.core.exceptions import ValidationError

from recipes.models import Ingredient, Tag


def ingredients_validator(ingredients):
    if not ingredients:
        raise ValidationError('Ингредиент не добавлен.')

    ing_list = []

    for ingredient in ingredients:
        if not Ingredient.objects.filter(id=ingredient['id'].id).exists():
            raise ValidationError('Такого ингредиента нет в базе.')

        if ingredient in ing_list:
            raise ValidationError('Такой ингридиент уже в списке.')
        ing_list.append(ingredient)

        if int(ingredient['amount']) <= 0:
            raise ValidationError('Количество не может быть 0 или меньше.')


def tags_validator(tags):
    if not tags:
        raise ValidationError('Нет тега.')

    tags_list = []

    for tag in tags:
        if not Tag.objects.filter(id=tag.id).exists():
            raise ValidationError('Такого тэга нет в базе.')

        if tag in tags_list:
            raise ValidationError('Такой тэг уже в списке.')
        tags_list.append(tag)
