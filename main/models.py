from django.contrib.auth import get_user_model
from django.db import models
from pytils.translit import slugify

MyUser = get_user_model()


class Genre(models.Model):
    image = models.ImageField(upload_to='genre_image')
    slug = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    premiere = models.DateTimeField(auto_now=True)
    budget = models.PositiveIntegerField()
    poster = models.ImageField(upload_to='poster')
    created = models.DateTimeField(auto_now_add=True)
    movie = models.FileField(upload_to='movie')

    def __str__(self):
        self.title

    class Meta:
        ordering = ('-created',)


class MovieImage(models.Model):
    image = models.ImageField(upload_to='movie_image', blank=True, null=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='images')


class Actor(models.Model):
    full_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='actors', blank=True, null=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='actors')

    def __str__(self):
        return self.full_name


class Comment(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments')
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"""{self.user}\t {self.created}\n\t{self.text}"""

    class Meta:
        ordering = ('-created',)


class Favorite(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorites')


class Like(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='likes')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='likes')


class Rating(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
