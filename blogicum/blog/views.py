from django.shortcuts import render, get_object_or_404, Http404, redirect
from django.utils import timezone
from .models import Post, Category
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.core.paginator import Paginator


class EditProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'username', 'email')
    template_name = 'registration/edit_profile.html'
    def test_func(self):
        return self.request.user == self.get_object()

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        posts = Post.objects.filter(author=user)
    else:
        posts = Post.objects.filter(author=user, is_published=True, pub_date__lte=timezone.now())
    posts = posts.order_by('-pub_date')
    paginator = Paginator(posts, settings.PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'show_edit_link': (request.user == user),
    }
    return render(request, 'blog/profile.html', context)


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/registration_form.html', {'form': form})


def index(request):
    posts = Post.objects.filter(is_published=True,
    pub_date__lte=timezone.now()).order_by('-pub_date')
    paginator = Paginator(posts, settings.PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, is_published=True)
    posts = Post.objects.filter(category=category,
    is_published=True, pub_date__lte=timezone.now()).order_by('-pub_date')
    paginator = Paginator(posts, settings.PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/category.html',
    {'category': category, 'page_obj': page_obj})


def post_detail(request, id, post_slug=None):
    template = 'blog/detail.html'
    now = timezone.now()

    try:
        post = Post.objects.get(
            pk=id,
            is_published=True,
            pub_date__lte=now,
            category__is_published=True
        )
        if post_slug and post.slug != post_slug:
            raise Http404("Неправильный slug для публикации.")

    except Post.DoesNotExist:
        raise Http404("Публикация не найдена или не соответствует критериям.")
    comments = post.comments.all()
    comment_form = CommentForm()
    context = {
        'post': post
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, template, context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if not post.pub_date:
                post.pub_date = timezone.now()
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form, 'is_edit': True})


@require_POST
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/edit_comment.html', {'form': form, 'comment': comment})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/detail.html', {'post': post, 'confirm_delete': True})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/detail.html', {
        'post': comment.post,
        'comment_to_delete': comment,
        'confirm_delete_comment': True,
    })
