# from django.shortcuts import render
#
# # Create your views here.
from django.views import generic
from rest_framework import viewsets, mixins

from main.models import Genre, Movie, Comment, Like, Favorite
from main.serializers import GenreSerializer, MovieSerializer, CommentSerializer, LikeSerializer, FavoriteSerializer, \
    RatingSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class LikeViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class FavoriteViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}


class RatingViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = RatingSerializer

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}
