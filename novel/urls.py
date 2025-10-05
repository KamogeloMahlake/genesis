from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("compose/<str:page>", views.compose, name="compose"),
    path("comments/<str:view>/<int:page_id>/<int:page_nr>", views.comments, name="comments"),
    path("like/<int:id>", views.like, name="like"),
    path("dislike/<int:id>", views.dislike, name="dislike"),
    path("editcomments/<int:id>", views.edit_comments, name="editcomments"),
    path("novels/<str:order>/<int:page_nr>", views.novels_view, name="novels"),
    path("chapters/<int:id>/<int:page_nr>", views.chapters_view, name="chapters"),
    path("novel/<int:id>", views.novel, name="novel"),
    path("chapter/<int:id>", views.chapter, name="chapter"),
    path("search/<int:page_nr>", views.search, name="search"),
    path("reply/<int:id>", views.reply, name="reply"),
    path("bookmark/<int:id>", views.bookmark, name="bookmark"),
]
