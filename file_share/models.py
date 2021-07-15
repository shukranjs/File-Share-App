from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from time import timezone

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.username


class Post(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    file_field = models.FileField(upload_to='uploads/')
    desc = models.TextField()

    # moderation's
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('file-detail', args=[self.pk])

    def __str__(self):
        return self.title


class Comment(models.Model):
    """ in this table you can store comment information """
    # relation's
    author = models.ForeignKey(User, verbose_name='Author', on_delete=models.CASCADE,
                               db_index=True, related_name='comments')

    post = models.ForeignKey(Post, verbose_name='Post', related_name='posts',
                             db_index=True, on_delete=models.CASCADE, )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    # information's
    content = models.TextField('Content', )

    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # moderation's
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.content
