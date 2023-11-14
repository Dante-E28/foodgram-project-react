from django.contrib import admin

from recipes.models import (Favorites, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'in_favorite'
    )
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')

    def in_favorite(self, obj):
        return obj.in_favorites.all().count()


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(Favorites)
admin.site.register(ShoppingCart)
admin.site.register(Subscribe)
