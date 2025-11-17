import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from novel.models import Comment, User, Novel, Chapter, Rating
from novel.forms import NewNovelForm, NewChapterForm, EditProfileForm
from novel.helpers import text_to_html, html_to_text
from statistics import fmean


@login_required
def delete_comment(request, id):
    comment = get_object_or_404(Comment, pk=id)
    if comment.user != request.user:
        return HttpResponseRedirect(reverse("index"))
    comment.delete()

    return HttpResponseRedirect(
        reverse("profile", kwargs={"username": request.user.username})
    )


@csrf_exempt
def rating(request, id):
    novel = get_object_or_404(Novel, pk=id)

    if request.method == "POST" and request.user.is_authenticated:
        if any(i.user == request.user for i in novel.novel_ratings.all()):
            return JsonResponse({"error": "Already made a rating"}, status=403)

        data = json.loads(request.body)

        story = int(data.get("story", False))
        characters = int(data.get("characters", False))
        world = int(data.get("world", False))
        writing = int(data.get("writing", False))

        if all([story, characters, world, writing]):
            try:
                rating = Rating(
                    novel=novel,
                    user=request.user,
                    story=story,
                    characters=characters,
                    world=world,
                    writing=writing,
                    average_rating=fmean([story, characters, world, writing]),
                )
                rating.save()
            except Exception:
                return JsonResponse(
                    {"error": "One of the fields is incorre"}, status=403
                )
            return JsonResponse(
                {
                    "story": fmean(
                        [rating.story for rating in novel.novel_ratings.all()]
                    ),
                    "characters": fmean(
                        [rating.characters for rating in novel.novel_ratings.all()]
                    ),
                    "world": fmean(
                        [rating.world for rating in novel.novel_ratings.all()]
                    ),
                    "writing": fmean(
                        [rating.writing for rating in novel.novel_ratings.all()]
                    ),
                    "average": fmean(
                        [rating.average_rating for rating in novel.novel_ratings.all()]
                    ),
                    "madeRating": True,
                    "count": novel.novel_ratings.count(),
                }
            )

        else:

            return JsonResponse({"error": "Invalid Form"}, status=403)

    if len(novel.novel_ratings.all()) > 0:
        return JsonResponse(
            {
                "story": fmean(
                    [
                        rating.story if rating else 0
                        for rating in novel.novel_ratings.all()
                    ]
                ),
                "characters": fmean(
                    [
                        rating.characters if rating else 0
                        for rating in novel.novel_ratings.all()
                    ]
                ),
                "world": fmean(
                    [
                        rating.world if rating else 0
                        for rating in novel.novel_ratings.all()
                    ]
                ),
                "writing": fmean(
                    [
                        rating.writing if rating else 0
                        for rating in novel.novel_ratings.all()
                    ]
                ),
                "average": fmean(
                    [
                        rating.average_rating if rating else 0
                        for rating in novel.novel_ratings.all()
                    ]
                ),
                "madeRating": any(
                    i.user == request.user for i in novel.novel_ratings.all()
                ) or not request.user.is_authenticated,
                "count": novel.novel_ratings.count(),
            }
        )
    return JsonResponse(
        {
            "story": 5,
            "characters": 5,
            "world": 5,
            "writing": 5,
            "average": 5,
            "madeRating": False,
            "count": 0,
        }
    )


def follow(request, username):
    user = get_object_or_404(User, username=username)
    if user == request.user:
        return JsonResponse({"error": "You can't follow yourself"}, status=403)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must login to follow"}, status=403)

    if request.user in user.followers.all():
        user.followers.remove(request.user)
    else:
        user.followers.add(request.user)

    return JsonResponse(
        {
            "follow": request.user in user.followers.all(),
            "followersCount": user.followers.count(),
            "followingCount": user.following.count(),
        }
    )

def profile(request, username):
    try:
        user = get_object_or_404(User, username=username)
        novels = Novel.objects.filter(user=user).order_by("-id")
        return render(
            request,
            "novel/profile.html",
            {
                "profile_user": user.serialize(request.user),
                "novels": [novel.serialize(request.user) for novel in novels],
                "is_own_profile": request.user == user,
            },
        )
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))


def edit_profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    user = request.user

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            try:

                form.save()

                return HttpResponseRedirect(
                    reverse("profile", kwargs={"username": user.username})
                )
            except IntegrityError:
                return render(
                    request,
                    "novel/edit_profile.html",
                    {"message": "Username already taken", "user": request.user},
                )
        else:
            return render(
                request,
                "novel/edit_profile.html",
                {
                    "form": EditProfileForm(
                        initial={
                            "username": user.username,
                            "email": user.email,
                            "gender": user.gender,
                            "location": user.location,
                            "date_of_birth": user.date_of_birth,
                            "about": user.about,
                            "user_image": user.user_image,
                        }
                    ),
                    "errors": form.errors,
                },
            )
    else:
        return render(
            request,
            "novel/edit_profile.html",
            {
                "form": EditProfileForm(
                    initial={
                        "username": user.username,
                        "email": user.email,
                        "gender": user.gender,
                        "location": user.location,
                        "date_of_birth": user.date_of_birth,
                        "about": user.about,
                        "user_image": user.user_image,
                    }
                )
            },
        )

def bookmarks(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    novels = request.user.bookmarks.all().order_by("-id")
    return render(
        request,
        "novel/bookmarks.html",
        {"novels": [novel.serialize(request.user) for novel in novels]},
    )


@csrf_exempt
@login_required
def create_chapter(request, id):
    if request.method == "POST":
        form = NewChapterForm(request.POST)
        novel = get_object_or_404(Novel, pk=id)

        if form.is_valid():
            chapter = Chapter(
                num=form.cleaned_data["num"],
                content=text_to_html(form.cleaned_data["content"]),
                title=form.cleaned_data["title"],
                novel=novel,
            )
            chapter.save()

            return HttpResponseRedirect(reverse("chapter", kwargs={"id": chapter.id}))

        else:
            return render(
                request,
                "novel/create_chapter.html",
                {"form": NewChapterForm(), "errors": form.errors},
            )

    return render(request, "novel/create_chapter.html", {"form": NewChapterForm()})


@csrf_exempt
@login_required
def edit_chapter(request, id):
    chapter = get_object_or_404(Chapter, pk=id)

    if request.method == "POST":
        form = NewChapterForm(request.POST)

        if form.is_valid():
            chapter.title = form.cleaned_data["title"]
            chapter.num = form.cleaned_data["num"]
            chapter.content = text_to_html(form.cleaned_data["content"])

            chapter.save()

            return HttpResponseRedirect(reverse("chapter", kwargs={"id": chapter.id}))

        else:
            return render(
                request,
                "novel/create_chapter.html",
                {
                    "form": NewChapterForm(
                        initial={
                            "title": chapter.title,
                            "num": chapter.num,
                            "content": html_to_text(chapter.content),
                        }
                    ),
                    "errors": form.errors,
                    "edit": True,
                    "id": chapter.id,
                },
            )

    return render(
        request,
        "novel/create_chapter.html",
        {
            "form": NewChapterForm(
                initial={
                    "title": chapter.title,
                    "num": chapter.num,
                    "content": html_to_text(chapter.content),
                }
            ),
            "edit": True,
            "id": chapter.id,
        },
    )


@csrf_exempt
@login_required(redirect_field_name=None, login_url="/login")
def create_novel(request):
    if request.method == "POST":
        form = NewNovelForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            genres = form.cleaned_data["genres"]
            novel_image = form.cleaned_data["novel_image"]

            novel = Novel(
                title=title,
                description=text_to_html(description),
                novel_image=novel_image,
                user=request.user,
            )
            novel.save()
            novel.genres.set(genres)
            novel.save()

            return HttpResponseRedirect(reverse("novel", kwargs={"id": novel.id}))
        else:
            return render(
                request,
                "novel/create_novel.html",
                {"form": NewNovelForm, "errors": form.errors},
            )
    return render(request, "novel/create_novel.html", {"form": NewNovelForm()})


@csrf_exempt
@login_required
def edit_novel(request, id):
    novel = get_object_or_404(Novel, pk=id)

    if request.method == "POST":
        form = NewNovelForm(request.POST, request.FILES)

        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            genres = form.cleaned_data["genres"]
            novel_image = form.cleaned_data["novel_image"]

            if title:
                novel.title = title
            if description:
                novel.description = text_to_html(description)
            if novel_image:
                novel.novel_image = novel_image

            if genres:
                novel.genres.clear()
                novel.genres.set(genres)
            novel.save()

            return HttpResponseRedirect(reverse("novel", kwargs={"id": id}))
        else:
            return render(
                request,
                "novel/create_novel.html",
                {
                    "form": NewNovelForm(
                        initial={
                            "title": novel.title,
                            "description": html_to_text(novel.description),
                            "genres": novel.genres.all(),
                            "novel_image": novel.novel_image,
                        }
                    ),
                    "edit": True,
                    "errors": form.errors,
                },
            )
    return render(
        request,
        "novel/create_novel.html",
        {
            "form": NewNovelForm(
                initial={
                    "title": novel.title,
                    "description": html_to_text(novel.description),
                }
            ),
            "edit": True,
        },
    )

@cache_page(60 * 10)
def search(request, page_nr=0):
    if page_nr > 0:
        query = request.GET.get("q")

        novels = Novel.objects.filter(title__icontains=query)
        try:
            c = Paginator(novels, 10)
            current_novels = c.page(page_nr)
        except Exception:
            return HttpResponseRedirect(reverse("index"))

        return render(
            request,
            "novel/search.html",
            {
                "query": query,
                "num": [i for i in range(1, c.num_pages + 1)],
                "current": page_nr,
                "novels": [
                    novel.serialize(request.user)
                    for novel in current_novels.object_list
                ],
                "last": c.num_pages,
            },
        )

    query = request.GET.get("q")
    novels = Novel.objects.filter(title__icontains=query)
    return JsonResponse(
        [novel.serialize(request.user) for novel in novels], status=200, safe=False
    )


@csrf_exempt
@login_required(redirect_field_name=None, login_url="/login")
def compose(request, page):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    data = json.loads(request.body)
    try:
        if data["text"]:
            if page == "novel":
                post = Comment(
                    user=request.user,
                    comment=data["text"],
                    novel=get_object_or_404(Novel, pk=int(data["id"])),
                )
            else:
                post = Comment(
                    user=request.user,
                    comment=data["text"],
                    chapter=get_object_or_404(Chapter, pk=int(data["id"])),
                )

            post.save()

            return JsonResponse({"message": "Comment successfully saved"}, status=201)
    except IndexError:
        return JsonResponse({"error": "Chapter or Novel DoesNotExist"})
    except Exception as e:
        return JsonResponse({"error": "Invalid"})
    return JsonResponse({"error": "Comment can not be empty"}, status=400)


@csrf_exempt
@login_required(redirect_field_name=None, login_url="/login")
def reply(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    data = json.loads(request.body)
    try:
        if data["text"]:
            parent = get_object_or_404(Comment, pk=id)
            post = Comment(
                user=request.user,
                comment=data["text"],
                parent_comment=parent,
            )

            post.save()

            return JsonResponse({"message": "Comment successfully saved"}, status=201)
    except Comment.DoesNotExist:
        return JsonResponse({"error": "Comment DoesNotExist"})
    except Exception as e:
        return JsonResponse({"error": str(e)})
    return JsonResponse({"error": "Comment can not be empty"}, status=400)


def comments(request, view, page_id, page_nr):
    comments = (
        Comment.objects.filter(novel=Novel.objects.get(pk=page_id))
        if view == "novel"
        else Comment.objects.filter(chapter=Chapter.objects.get(pk=page_id))
    )

    c = Paginator(comments.order_by("-id"), 10)
    current_comments = c.page(page_nr)

    return JsonResponse(
        {
            "num": [i for i in range(1, c.num_pages + 1)],
            "current": page_nr,
            "comments": [
                comment.serialize(request.user)
                for comment in current_comments.object_list
            ],
            "user": True if request.user.username else False,
        },
        safe=False,
    )


def like(request, id):
    comment = get_object_or_404(Comment, pk=id)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not login"}, status=400)

    if request.user in comment.like.all():
        comment.like.remove(request.user)
    else:
        if request.user in comment.dislike.all():
            comment.dislike.remove(request.user)
        comment.like.add(request.user)

    return JsonResponse({"message": "Like has been removed/added"})


def dislike(request, id):
    comment = get_object_or_404(Comment, pk=id)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not login"}, status=400)

    if request.user in comment.dislike.all():
        comment.dislike.remove(request.user)
    else:
        if request.user in comment.like.all():
            comment.like.remove(request.user)
        comment.dislike.add(request.user)

    return JsonResponse({"message": "Dislike has been removed/added"})


def edit_comments(request, id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required"}, status=400)

    if not request.user.username:
        return JsonResponse({"error": "User must login"}, status=400)

    try:
        comment = get_object_or_404(Comment, pk=id)

        if comment.user != request.user:
            return JsonResponse({"error": "Not allowed to edit comment"}, status=401)

        data = json.loads(request.body)

        if data["text"]:
            comment.text = data["text"]
            comment.save()

            return JsonResponse({"success": "Successfull edit"}, status=201)

        return JsonResponse({"error": "Put can not be empty"}, status=400)

    except Comment.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)


def bookmark(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User must login"}, status=400)
    try:
        novel = get_object_or_404(Novel, pk=id)

        if novel in request.user.bookmarks.all():
            request.user.bookmarks.remove(novel)
            return JsonResponse({"message": "Removed"}, status=200)
        else:
            request.user.bookmarks.add(novel)
            return JsonResponse({"message": "Added"}, status=200)
    except Novel.DoesNotExist:
        return JsonResponse({"error": "Novel does not exist"}, status=404)

#@cache_page(60 * 10)
def index(request):
    novels = Novel.objects.all()
    lastest = novels.order_by("-date")[:9]
    popular = novels.order_by("-views")[:9]
    return render(
        request,
        "novel/index.html",
        {
            "recent_chapters": [
                chapter.serialize()
                for chapter in Chapter.objects.all().order_by("-id")[:10]
            ],
            "lastest": [n.serialize(request.user) for n in lastest],
            "popular": [n.serialize(request.user) for n in popular],
        },
    )

#@cache_page(60 * 60)
def novels_view(request, order, page_nr):
    try:
        novels = Novel.objects.all().order_by(f"{order}")
        n = Paginator(novels, 10)
        current_novels = n.page(page_nr)

        return render(
            request,
            "novel/novels.html",
            {
                "novels": [
                    novel.serialize(request.user)
                    for novel in current_novels.object_list
                ],
                "num": [i for i in range(1, n.num_pages + 1) if abs(i - page_nr) < 5],
                "last": n.num_pages,
                "title": f"Novels | Page {page_nr}  ",
                "current": page_nr,
                "order": order,
            },
        )

    except EmptyPage:
        return HttpResponseRedirect(reverse(index))


def chapters_view(request, id, page_nr):
    try:
        n = get_object_or_404(Novel, pk=id)
        chapters = Chapter.objects.filter(novel=n).order_by("num")
        c = Paginator(chapters, 100)
        current_chapters = c.page(page_nr)

        return render(
            request,
            "novel/chapters.html",
            {
                "title": f"{n.title} | Page {page_nr}",
                "chapters": [
                    chapter.serialize() for chapter in current_chapters.object_list
                ],
                "last": c.num_pages,
                "current": page_nr,
                "num": [i for i in range(1, c.num_pages + 1) if abs(i - page_nr) < 5],
                "id": id,
                "name": n.title,
                "is_author": n.user == request.user,
            },
        )
    except EmptyPage:
        return HttpResponseRedirect(reverse(novel, kwargs={"id": id}))

#@cache_page(60 * 10)
def novel(request, id):
    novel = get_object_or_404(Novel, pk=id)
    chapters = Chapter.objects.filter(novel=novel).order_by("num")[:20]

    if len(novel.novel_ratings.all()) > 0:
        rating = {
            "story": fmean(
                [
                    rating.story if rating.story else 0
                    for rating in novel.novel_ratings.all()
                ]
            ),
            "characters": fmean(
                [
                    rating.characters if rating.characters else 0
                    for rating in novel.novel_ratings.all()
                ]
            ),
            "world": fmean(
                [
                    rating.world if rating.world else 0
                    for rating in novel.novel_ratings.all()
                ]
            ),
            "writing": fmean(
                [
                    rating.writing if rating.writing else 0
                    for rating in novel.novel_ratings.all()
                ]
            ),
            "average": fmean(
                [
                    rating.average_rating if rating.average_rating else 0
                    for rating in novel.novel_ratings.all()
                ]
            ),
        }

    print(novel.novel_ratings.all())
    return render(
        request,
        "novel/novel.html",
        {
            "novel": novel.serialize(request.user),
            "chapters": [chapter.serialize() for chapter in chapters],
            "chapter_id": chapters[0].id if chapters else 0,
            "bookmark": (
                novel in request.user.bookmarks.all()
                if request.user.is_authenticated
                else False
            ),
            "rating": rating if len(novel.novel_ratings.all()) > 0 else {},
        },
    )

#@cache_page(60 * 10)
def chapter(request, id):
    chap = get_object_or_404(Chapter, pk=id)
    novel = get_object_or_404(Novel, pk=chap.novel.id)
    novel.views += 1
    chap.views += 1

    novel.save()
    chap.save()
    return render(
        request,
        "novel/chapter.html",
        {
            "chapter": chap.view(),
        },
    )


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "novel/login.html",
                {"message": "Invalid username and/or password"},
            )
    else:
        return render(request, "novel/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(
                request, "novel/register.html", {"message": "Passwords must match"}
            )

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "novel/register.html", {"message": "Username already taken"}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "novel/register.html")


@login_required
def delete(request, view, id):

    object = (
        get_object_or_404(Novel, pk=id)
        if view == "novel"
        else get_object_or_404(Chapter, pk=id)
    )
    user = object.user if view == "novel" else object.novel.user
    if request.user != user:
        return HttpResponseRedirect(reverse("index"))
    object.delete()
    if view == "novel":
        return HttpResponseRedirect(
            reverse("profile", kwargs={"username": user.username})
        )
    return HttpResponseRedirect(
        reverse("chapters", kwargs={"id": object.novel.id, "page_nr": 1})
    )
