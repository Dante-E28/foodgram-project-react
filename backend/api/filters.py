import django_filters as filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = filters.NumberFilter(
        method='filter_is_favorited'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(in_shopping_cart__user=self.request.user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(in_favorites__user=self.request.user)
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istarstwith')

    class Meta:
        model = Ingredient
        fields = ('name',)
