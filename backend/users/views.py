from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Subscribe
from users.serializers import (SubscribeSerializer, UserPostSerializer,
                               UserSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserPostSerializer
        return UserSerializer

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.data.get('new_password'))
        user.save()
        return Response(
            'Пароль успешно изменен',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, *args, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            if Subscribe.objects.filter(author=author, user=user).exists():
                return Response(
                    'Вы уже подписаны.',
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    'Нельзя подписаться на себя.',
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = SubscribeSerializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if Subscribe.objects.filter(author=author, user=user).exists():
            Subscribe.objects.filter(author=author, user=user).first().delete()
            return Response(
                'Вы отписаны от автора.',
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {'errors': 'Такой подписки нет.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = self.request.user
        authors = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(authors)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
