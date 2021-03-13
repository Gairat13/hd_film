from rest_framework import serializers

from main.models import Genre, Movie, MovieImage, Comment, Like, Favorite, Rating
from django.db.models import Avg


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Genre
        fields = ('title', 'image', 'slug')

    def get_fields(self):
        fields = super().get_fields()
        action = self.context.get('action')
        if action in ['create', 'update']:
            fields.pop('slug')
        return fields

    def create(self, validated_data):
        genre = Genre.objects.create(**validated_data)
        return genre

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieImage
        fields = ('image',)

    def _get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            url = obj.image.url
            if request is not None:
                url = request.build_absolute_uri(url)
            return url
        return ''

    def to_representation(self, instance):
        representation = super(ImageSerializer, self).to_representation(instance)
        representation['image'] = self._get_image_url(instance)
        return representation


class MovieSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format='%d %B %Y %H:%M', read_only=True)
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = '__all__'

    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'list' or action == 'search':
            fields.pop('images')
            fields.pop('created')
            fields.pop('description')
            fields.pop('movie')
            fields.pop('budget')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        images_data = request.FILES
        movie = Movie.objects.create(**validated_data)
        for image in images_data.getlist('images'):
            MovieImage.objects.create(movie=movie, image=image)
        return movie

    def update(self, instance, validated_data):
        request = self.context.get('request')

        for k, v in validated_data.items():
            setattr(instance, k, v)

        instance.images.all().delete()
        images_data = request.FILES
        for image in images_data.getlist('images'):
            MovieImage.objects.create(movie=instance, image=image)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        action = self.context.get('action')

        rating = instance.ratings.all().aggregate(Avg('rating')).get('rating__avg')
        like = LikeSerializer(instance.likes.filter(like=True), many=True, context=self.context).data
        comment = CommentSerializer(instance.comments.all(), many=True,
                                    context=self.context).data
        representation['like'] = len(like)
        representation['comment'] = len(comment)
        representation['rating'] = rating if rating != None else 0

        if action == 'detail':
            representation['images'] = ImageSerializer(instance.images.all(), many=True, context=self.context).data
            representation['genre'] = GenreSerializer(instance.genre).data
            representation['rating'] = RatingSerializer(instance.ratings.all(), many=True, context=self.context).data
            representation['comments'] = comment
            representation['like'] = like
        return representation


class CommentSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format='%d %B %Y %H:%M', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'movie', 'created', 'user', 'parent')

    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'create' or action == 'update':
            fields.pop('user')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        comment = Comment.objects.create(user=user, **validated_data)
        return comment

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['children'] = CommentSerializer(instance.children.all(), many=True, context=self.context).data
        return representation


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'movie', 'user', 'like')

    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'create':
            fields.pop('user')
            fields.pop('like')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        movie = validated_data.get('movie')
        like = Like.objects.get_or_create(user=user, movie=movie)[0]
        like.like = True if like.like == False else False
        like.save()
        return like


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('id', 'movie', 'user', 'favorite')

    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'create':
            fields.pop('user')
            fields.pop('favorite')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        movie = validated_data.get('movie')
        favorite = Favorite.objects.get_or_create(user=user, movie=movie)[0]
        favorite.favorite = True if favorite.favorite == False else False
        favorite.save()
        return favorite


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('movie', 'user', 'rating')

    def validate(self, attrs):
        rating = attrs.get('rating')
        if rating > 5:
            raise serializers.ValidationError('The value must not exceed 5')
        return attrs

    def get_fields(self):
        fields = super().get_fields()
        action = self.context.get('action')
        if action == 'create':
            fields.pop('user')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        movie = validated_data.get('movie')
        rat = validated_data.get('rating')
        rating = Rating.objects.get_or_create(user=user, movie=movie)[0]
        rating.rating = rat
        rating.save()
        return rating
