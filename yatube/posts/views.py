from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    template = "posts/index.html"
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAR_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    title = "Последние обновления на сайте"
    context = {
        "page_obj": page_obj,
        "title": title,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    group_post_list = group.posts.all()
    paginator = Paginator(group_post_list, settings.PAR_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    title = f"Записи сообщества {group}"
    context = {
        "group": group,
        "page_obj": page_obj,
        "title": title,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    title = f"Профайл пользователя {author}"
    template = "posts/profile.html"
    profile_posts_list = author.posts.all()
    counter_posts = profile_posts_list.count()
    paginator = Paginator(profile_posts_list, settings.PAR_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    )
    followers_count = author.following.count()
    following_count = author.follower.count()
    context = {
        "title": title,
        "page_obj": page_obj,
        "counter_posts": counter_posts,
        "author": author,
        "following": following,
        "followers_count": followers_count,
        "following_count": following_count,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"
    post = get_object_or_404(Post, id=post_id)
    title = post.text
    counter_posts = post.author.posts.count()
    form = CommentForm()
    comments = post.comments.all()
    context = {
        "title": title,
        "post": post,
        "counter_posts": counter_posts,
        "form": form,
        "comments": comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", request.user)
    template = "posts/post_create.html"
    context = {"form": form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    edit = True
    template = "posts/post_create.html"
    context = {
        "post": post,
        "form": form,
        "edit": edit,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts_list, settings.PAR_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    template = "posts/follow.html"
    title = "Подписки"
    context = {
        "page_obj": page_obj,
        "paginator": paginator,
        "title": title,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    follow_user = get_object_or_404(User, username=username)
    if request.user != follow_user:
        Follow.objects.get_or_create(user=request.user, author=follow_user)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    unfollow_user = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=unfollow_user).delete()
    return redirect("posts:profile", username=username)
