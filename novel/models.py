from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    user_image = models.ImageField(upload_to="user-images/")
    bookmarks = models.ManyToManyField(
        "Novel", related_name="bookmark_by", blank=True
    ) 

class Novel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_created_novels",
        blank=True,
        null=True,
    )
    creator = models.CharField(max_length=50, default="Admin", blank=True, null=True)
    title = models.CharField(max_length=1000, unique=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    novel_image = models.ImageField(upload_to="novel-images/", blank=True, null=True)
    status = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "image": self.novel_image.url if self.novel_image else None,
            "comments": self.novel_comments.count(),
            "views": sum(chapter.views for chapter in self.chapters.all()),
            "latest_chapter": self.chapters.order_by("-num").first().num
            if self.chapters.exists()
            else None,
            "tags": [tag.name for tag in self.tags.all()],
            "genres": [genre.name for genre in self.genres.all()],
            "average_rating": round(
                sum(rating.rating for rating in self.novel_ratings.all())
                / self.novel_ratings.count(),
                1,
            )
            if self.novel_ratings.exists()
            else None,
        }


class Chapter(models.Model):
    title = models.TextField()
    num = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    content = models.TextField()
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name="chapters")
    views = models.IntegerField(default=0, blank=True, null=True)

    def serialize(self):
        return {
            "id": self.id,
            "novel_name": self.novel.title,
            "novel_image_url": (
                self.novel.novel_image.url if self.novel.novel_image else None
            ),
            "title": self.title,
            "num": self.num,
            "date": (timezone.now().date() - self.date).days,
            "views": self.views,
            "comments": self.chapter_comments.count(),

        }

    def view(self):
        try:
            previous = Chapter.objects.filter(num=self.num - 1, novel=self.novel)[0].id

        except IndexError:
            previous = None

        try:
            next = Chapter.objects.filter(num=self.num + 1, novel=self.novel)[0].id

        except IndexError:
            next = None

        return {
            "id": self.id,
            "novel_name": self.novel.title,
            "novel_id": self.novel.id,
            "title": self.title,
            "num": self.num,
            "content": self.content,
            "views": self.views,
            "previous": previous,
            "next": next,
        }


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_comments"
    )
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="chapter_comments",
        blank=True,
        null=True,
    )
    novel = models.ForeignKey(
        Novel,
        on_delete=models.CASCADE,
        related_name="novel_comments",
        blank=True,
        null=True,
    )
    comment = models.TextField()
    date = models.DateField(auto_now_add=True)
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )
    like = models.ManyToManyField(User, related_name="likes", blank=True)
    dislike = models.ManyToManyField(User, related_name="dislikes", blank=True)

    def serialize(self, user):
        return {
            "id": self.id,
            "user": self.user.username,
            "comment": self.comment,
            "date": self.date,
            "likesCount": self.like.count(),
            "dislikesCount": self.dislike.count(),
            "liked": user.is_authenticated and self.like.filter(id=user.id).exists(),
            "disliked": user.is_authenticated and self.dislike.filter(id=user.id).exists(),
            "isAuthor": user == self.user,
            "replies": [reply.serialize(user) for reply in self.replies.all()],        
        }   

class Tag(models.Model):
    name = models.CharField(max_length=100)
    novel = models.ManyToManyField(Novel, related_name="tags", blank=True)


class Genre(models.Model):
    name = models.CharField(max_length=100)
    novel = models.ManyToManyField(Novel, related_name="genres", blank=True)


class Rating(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_ratings"
    )
    novel = models.ForeignKey(
        Novel, on_delete=models.CASCADE, related_name="novel_ratings"
    )
    rating = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
