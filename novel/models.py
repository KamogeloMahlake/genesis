from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    user_image = models.ImageField(upload_to="user-images/", null=True, blank=True)
    bookmarks = models.ManyToManyField(
        "Novel", related_name="bookmark_by", blank=True
    ) 
    gender = models.CharField(max_length=6, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    followers = models.ManyToManyField("self", related_name="following", blank=True, symmetrical=False)

    def serialize(self, user):
        return {
            "id": self.id,
            "username": self.username,
            "image": self.user_image.url if self.user_image else "/media/placeholder.png",
            "gender": self.gender if self.gender else '--',
            "date_joined": self.date_joined,
            "comments_count": self.user_comments.count(),
            "comments": [comment.serialize(user) for comment in self.user_comments.all()],
            "followers_count": self.followers.count(),
            "following_count": self.following.count(),
            "is_following": user in self.followers.all(),
            "birthday": self.date_of_birth if self.date_of_birth else '--',
            "location": self.location if self.location else '--',
            "about": self.about,
            "novel_comments": sum(novel.novel_comments.count() for novel in self.user_created_novels.all()),
            "total_views": sum(sum(chapter.views for chapter in novel.chapters.all()) for novel in self.user_created_novels.all()),
            "last_login": self.last_login,
            "is_user": user == self,
        }

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
    date = models.DateTimeField(auto_now_add=True)
    novel_image = models.ImageField(upload_to="novel-images/", blank=True, null=True)
    status = models.BooleanField(default=False)

    def serialize(self, user):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "image": self.novel_image.url if self.novel_image else '/media/placeholder.png',
            "comments": self.novel_comments.count(),
            "total_comments": self.novel_comments.count() + sum(chapter.chapter_comments.count() for chapter in self.chapters.all()),
            "views": sum(chapter.views for chapter in self.chapters.all()) ,
            "latest_chapter": self.chapters.order_by("-num").first().num
            if self.chapters.exists()
            else None,
            "tags": [tag.name for tag in self.tags.all()],
            "genres": [genre.name for genre in self.genres.all()],
            "average_rating": round(
                sum(rating.average_rating for rating in self.novel_ratings.all())
                / self.novel_ratings.count(),
                1,
            )
            if self.novel_ratings.exists()
            else None,
            "status": self.status,
            "num": self.chapters.count(),
            "date": self.date,
            "author": self.user.username if self.user else 'Unknown',
            "is_author": self.user == user
        }


class Chapter(models.Model):
    title = models.TextField()
    num = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
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
    date = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )
    like = models.ManyToManyField(User, related_name="likes", blank=True)
    dislike = models.ManyToManyField(User, related_name="dislikes", blank=True)

    def serialize(self, user):
        return {
            "id": self.id,
            "user": self.user.username,
            "image": self.user.user_image.url if self.user.user_image else '/media/placeholder.png',
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

    def serialize(self):
        return (
            self.id, self.name
        )

class Rating(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_ratings"
    )
    novel = models.ForeignKey(
        Novel, on_delete=models.CASCADE, related_name="novel_ratings"
    )
    story = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    writing = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    world = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    characters = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    average_rating = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

class Message(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey("User", on_delete=models.PROTECT, related_name="messages_sent")
    recipient = models.ManyToManyField("User", related_name="message_recieved")
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    parent_message = models.ForeignKey("self", blank=True, on_delete=models.PROTECT, related_name="replys")

    def send_message(from_user, to_user, body, parent=None):
        sender_message = Message(user=from_user, sender=from_user, recipient=to_user, body=body, parent_message=parent)
        sender_message.save()

    