from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger, Paginator
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST                                           
from django.views.generic import ListView
from .forms import CommentForm, EmailPostForm
from .models import Post


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST': 
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                    f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                    f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject=subject,
                       message=message,
                        from_email= 'none',
                        recipient_list=[cd['to']])
            sent = True 
            # ... send email
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html',{'post': post,
                                                     'form': form,
                                                    'sent':sent})
class PostListView(ListView):
    """
    Alternative Post ListView
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
                                            

def post_list(request):
    post_list = Post.published.all()

    paginator = paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger :
       
        posts = paginator.page(1)
    except EmptyPage:
        
        posts = paginator.page(paginator.num_pages) 
    return render(request,
                'blog/post/list.html',
                {'posts': posts})

 

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()

    return render(
            request,
            'blog/post/detail.html',
            {
                'post': post,
                'comments':comments,
                'form':form
            }
        )

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
            comment = form.save(commit=False)
            #Assign the post to the comment
            comment.post = post
            # Save the comment to the database
            comment.save()
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
            
            
    )