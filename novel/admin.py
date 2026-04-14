from django.contrib import admin
from novel.models import Chapter, Comment, Genre, Novel, Rating, Tag, User


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "gender", "date_of_birth", "location")


class NovelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "creator",
        "date",
        "status",
        "views",
        "display_chapters",
        "last_chapter_scraped",
        "fanfic_id",
        "ao3_id",
    )


class ChapterAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "display_novel",
        "num",
    )


admin.site.register(User, UserAdmin)
admin.site.register(Novel, NovelAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Genre)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(Rating)
