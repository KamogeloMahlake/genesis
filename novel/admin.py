from django.contrib import admin
from novel.models import Chapter, Comment, Genre, Novel, Rating, Tag, User

admin.site.register(User)
admin.site.register(Novel)
admin.site.register(Chapter)
admin.site.register(Genre)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(Rating)
