from django.db.models import Count
from django.urls import reverse_lazy
from taggit.models import Tag

from blog.models import Post, Comment
from django.core.mail import send_mail
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class PostListView(ListView):
    """class view all posts in blog"""
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2
    template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 2)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    context = {
        'posts': posts,
        'page': page,
        'tag': tag,
    }
    return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return redirect(reverse_lazy('blog:post_list'))

    else:
        comment_form = CommentForm()
    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                        .order_by('-same_tags', '-publish')[:4]
    context = {
        'post': post,
        'comment_form': comment_form,
        'new_comment': new_comment,
        'comments': comments,
        'similar_posts': similar_posts
    }

    return render(request, 'blog/post/detail.html', context)


def post_share(request, post_id):
    # Retrieve post id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f'{cd["name"]} Recommends you read {post.title}'
            message = f"Read {post.title}\n\n   {post_url}\n\n " \
                      f"{cd['name']} comments {cd['comments']}"
            mail_to = f"{cd['email']}subject------------"
            to = f"{cd['to']}"
            send_mail(subject, message, mail_to, [to])
            sent = True
    else:
        form = EmailPostForm()
    context = {
        'form': form,
        'post': post,
        'sent': sent,
    }
    return render(request, 'blog/post/share.html', context)
