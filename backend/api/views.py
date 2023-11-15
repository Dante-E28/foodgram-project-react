from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (FavoritesSerializer, IngredientSerializer,
                             RecipeSerializer, ShoppingCartSerializer,
                             TagSerializer)
from recipes.models import Favorites, Ingredient, Recipe, ShoppingCart, Tag
from services.utils import download_txt_cart


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, *args, **kwargs):
        user = self.request.user

        try:
            recipe = Recipe.objects.get(id=kwargs['pk'])
        except Recipe.DoesNotExist:
            if request.method == 'POST':
                return Response(
                    'Такого рецепта нет.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                'Такого рецепта нет.',
                status=status.HTTP_404_NOT_FOUND
            )
        if request.method == 'POST':
            if Favorites.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    'Рецепт уже в избраном.',
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = FavoritesSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        if Favorites.objects.filter(user=user, recipe=recipe).exists():
            Favorites.objects.filter(user=user, recipe=recipe).first().delete()
            return Response(
                'Рецепт удален из избраного.',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            'Такого рецепта нет в избраном.',
            status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, **kwargs):
        user = self.request.user

        try:
            recipe = Recipe.objects.get(id=kwargs['pk'])
        except Recipe.DoesNotExist:
            if request.method == 'POST':
                return Response(
                    'Такого рецепта нет.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                'Такого рецепта нет.',
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    'Рецепт уже в списке.',
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = ShoppingCartSerializer(
                data=request.data
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            ShoppingCart.objects.filter(
                user=user, recipe=recipe).first().delete()
            return Response(
                'Рецепт удален из списка.',
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            'Такого рецепта нет в списке.',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        if user.shopping_cart.exists():
            cart = user.shopping_cart.all()
            return download_txt_cart(cart)
        return Response('Список пуст.', status=status.HTTP_400_BAD_REQUEST)
