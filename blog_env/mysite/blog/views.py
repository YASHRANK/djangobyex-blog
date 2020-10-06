from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from taggit.models import Tag

from .forms import CommentForm, EmailPostForm, SearchForm

from.models import Post, Comment


def post_list(request, tag_slug=None):
    post_obj_list = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_obj_list = post_obj_list.filter(tags__in=[tag])

    paginator = Paginator(post_obj_list, 3)  # paginate by 4 posts
    page = request.GET.get('page')  # get the number of requested page
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts,
                                                   'page': page,
                                                   'tag': tag, })


def post_detail(request, post):
    post = get_object_or_404(Post, slug=post, status='published', )
# for handling comments
    comments = post.comments.filter(active=True)
    new_commnet = None

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_commnet = comment_form.save(commit=False)
            new_commnet.post = post
            new_commnet.save()
    else:
        comment_form = CommentForm()

# similar posts

    # return array of current post's all tags

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids).exclude(id=post.id)  # filtering similar post from piblished posts - current one
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'new_comment': new_commnet, 'comment_form': comment_form, 'similar_posts': similar_posts})


def post_share(request, slug):

    post = get_object_or_404(Post, slug=slug, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data  # dict
            # ....send mail
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read - {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments:\n {cd['comments']}"
            send_mail(subject, message, 'info.devblogs@gmail.com', [cd['to']])

            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    tags = Tag.objects.all()

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # search vector for lookup fields
            search_vector = SearchVector(
                'title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)

            # TRIGRAM SIMILARITY
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')

            # RANKING WITH TS_VECTOR
            # results = Post.published.annotate(
            #     search=search_vector,
            #     rank=SearchRank(search_vector, search_query)
            # ).filter(rank__gte=0.3).order_by('-rank')

    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results, 'tags': tags})
