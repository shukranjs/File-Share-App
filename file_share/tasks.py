from celery import shared_task
from . models import Post
from datetime import timedelta, datetime

delta = datetime.today() - timedelta(days=1)
delete_posts = Post.objects.filter(created_at__gt=delta)
@shared_task
def delete_post():
    delete_posts.delete()