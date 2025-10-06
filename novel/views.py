import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from novel.models import Comment, User, Novel, Chapter
from novel.forms import NewNovelForm

def profile(request, username):
    try:
        user = User.objects.get(username=username)
        comments = Comment.objects.filter(user=user)
        novels = Novel.objects.filter(user=user).order_by('-id')
        return render(
            request, 
            "novel/profile.html", 
            {
                "user": user, 
                "novels": [novel.serialize() for novel in novels], 
                "is_own_profile": request.user == user,
                "comments_count": len(comments),
                "comments": [comment.serialize(request.user) for comment in comments]
            })
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))

def edit_profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(
                request, "novel/edit_profile.html", {"message": "Passwords must match", "user": request.user}
            )

        try:
            user = User.objects.get(pk=request.user.id)
            user.username = username
            user.email = email
            if password:
                user.set_password(password)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse("profile", kwargs={"username": user.username}))
        except IntegrityError:
            return render(
                request, "novel/edit_profile.html", {"message": "Username already taken", "user": request.user}
            )
    else:
        return render(request, "novel/edit_profile.html", {"user": request.user})

def bookmarks(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    novels = request.user.bookmarks.all().order_by('-id')
    return render(request, "novel/bookmarks.html", {"novels": [novel.serialize() for novel in novels]})    

@csrf_exempt
@login_required(redirect_field_name=None, login_url='/login')
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
                description=description,
                novel_image=novel_image,
                user=request.user
            )
            novel.save()
            novel.genres.set(genres)
            novel.save()

            return HttpResponseRedirect(reverse("novel", kwargs={"id": novel.id}))
        else:
            return render(request, "novel/create_novel.html", {"form": NewNovelForm, "errors": form.errors})
    return render(request, "novel/create_novel.html", {"form": NewNovelForm()})

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
                "novels": [novel.serialize() for novel in current_novels.object_list],
                "last": c.num_pages
            },
        )

    query = request.GET.get("q")
    novels = Novel.objects.filter(title__icontains=query)
    return JsonResponse([novel.serialize() for novel in novels], status=200, safe=False)

@csrf_exempt
@login_required(redirect_field_name=None, login_url='/login')
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
                    novel=Novel.objects.filter(pk=int(data["id"]))[0]
                )
            else:
                post = Comment(
                    user=request.user,
                    comment=data["text"],
                    chapter=Chapter.objects.filter(pk=int(data["id"]))[0]
            )

            post.save()

            return JsonResponse({"message": "Comment successfully saved"}, status=201)
    except IndexError:
        return JsonResponse({"error": "Chapter or Novel DoesNotExist"})
    except Exception as e:
        return JsonResponse({"error": "Invalid"})
    return JsonResponse({"error": "Comment can not be empty"}, status=400)

@csrf_exempt
@login_required(redirect_field_name=None, login_url='/login')
def reply(request, id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    data = json.loads(request.body)
    try: 
        if data["text"]:
            parent = Comment.objects.get(pk=id)
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

def comments(request, view, page_id,page_nr):
    comments = Comment.objects.filter(novel=Novel.objects.get(pk=page_id)) if view == "novel" else Comment.objects.filter(chapter=Chapter.objects.get(pk=page_id))
        
    c = Paginator(comments.order_by('-id'), 10)
    current_comments = c.page(page_nr)

    return JsonResponse(
        {
             
            "num": [i for i in range(1, c.num_pages + 1)], 
            "current": page_nr,
            "comments": [comment.serialize(request.user) for comment in current_comments.object_list],
            "user": True if request.user.username else False,
        }, safe=False
    )


def like(request, id):
    comment = Comment.objects.get(pk=id)
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
    comment = Comment.objects.get(pk=id)
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
        comment = Comment.objects.get(pk=id)

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
        novel = Novel.objects.get(pk=id)

        if novel in request.user.bookmarks.all():
            request.user.bookmarks.remove(novel)
            return JsonResponse({"message": "Removed"}, status=200)
        else:
            request.user.bookmarks.add(novel)
            return JsonResponse({"message": "Added"}, status=200)
    except Novel.DoesNotExist:
        return JsonResponse({"error": "Novel does not exist"}, status=404)
    
def index(request):
    return render(
        request,
        "novel/index.html",
        {
            "novels": [novel.serialize() for novel in Novel.objects.all().order_by("-id")[:3]],
            "recent_chapters": [
                chapter.serialize()
                for chapter in Chapter.objects.all().order_by("-id")[:10]
            ],
        },
    )


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
                    novel.serialize() for novel in current_novels.object_list
                ],
                "num": [i for i in range(1, n.num_pages + 1) if abs(i - page_nr) < 5 ], 
                "last": n.num_pages,
                "title": f"Novels | Page {page_nr}  ",
                "current": page_nr,
                "order": order
            
            },
        )

    except EmptyPage:
        return HttpResponseRedirect(reverse(index))


def chapters_view(request, id, page_nr):
    try:
        n = Novel.objects.get(pk=id)
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
                "num": [i for i in range(1, c.num_pages + 1) if abs(i - page_nr) < 5 ],
                "id": id,
                "name": n.title
            },
        )
    except EmptyPage:
        return HttpResponseRedirect(reverse(novel, kwargs={'id': id}))


def novel(request, id):
    n = Novel.objects.get(pk=id)
    c = Comment.objects.filter(novel=n)
    chapters = Chapter.objects.filter(novel=n).order_by("num")[:20]
    return render(
        request, "novel/novel.html", {"novel": n.serialize(), "comments": c, "chapters": [chapter.serialize() for chapter in chapters], "chapter_id": chapters[0].id if chapters else 0, "bookmark": n in request.user.bookmarks.all() if request.user.is_authenticated else False}
    )


def chapter(request, id):
    chap = Chapter.objects.get(pk=id)
    c = Comment.objects.filter(chapter=chap)
    chap.views += 1

    chap.save()
    return render(
        request, "novel/chapter.html", {"chapter": chap.view(), "comments": c}
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
