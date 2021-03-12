from django.contrib import admin
from main.models import *


class GenreAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    list_display = ('title', 'slug')
    list_display_links = ('title',)


admin.site.register(Comment)
admin.site.register(Actor)
admin.site.register(Movie)
admin.site.register(Genre, GenreAdmin)