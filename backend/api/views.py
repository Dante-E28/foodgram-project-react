from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginations import CustomPagination
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (FavoritesSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeWriteSerializer,
                             ShoppingCartSerializer, TagSerializer)
from recipes.models import Favorites, Ingredient, Recipe, ShoppingCart, Tag
from services.utils import download_txt_cart


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @staticmethod
    def _handle_favorite_or_cart(self, request, pk, model_class,
                                 serializer_class, message):
        user = self.request.user

        try:
            recipe = Recipe.objects.get(id=pk)
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
            if model_class.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    message['already_exists'],
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Проверка для соответсвия документации api.
        if not model_class.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                message['not_found'],
                status=status.HTTP_400_BAD_REQUEST
            )

        model_class.objects.filter(user=user, recipe=recipe).delete()
        return Response(
            message['deleted'],
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, **kwargs):
        message = {
            'not_found': 'Такого рецепта нет в избранном.',
            'already_exists': 'Рецепт уже в избраном.',
            'deleted': 'Рецепт удален из избраного.'
        }
        return self._handle_favorite_or_cart(self, request, kwargs['pk'],
                                             Favorites, FavoritesSerializer,
                                             message)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, **kwargs):
        message = {
            'not_found': 'Такого рецепта нет в списке.',
            'already_exists': 'Рецепт уже в списке.',
            'deleted': 'Рецепт удален из списка.'
        }
        return self._handle_favorite_or_cart(self, request, kwargs['pk'],
                                             ShoppingCart,
                                             ShoppingCartSerializer, message)

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
