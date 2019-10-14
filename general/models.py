from django.db import models
from .interface import DescribedModel, BaseModel
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from uuid import uuid4
from sorl.thumbnail import delete
from django.core.exceptions import ValidationError
import os


# Create your models here.

def validate_file_size(value):
    file_size = value.size

    if file_size > 10485760:
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    else:
        return value


def validate_video_file_size(value):
    file_size = value.size

    if file_size > 100 * 1024 ** 2:
        raise ValidationError("The maximum video file that can be uploaded is 100MB")
    else:
        return value


def path_and_rename(instance, filename):
    # now = datetime.datetime.now()
    # upload_to = 'images/' + str(now.year) + '/' + str(now.month) + '/' + str(now.day) + '/'
    upload_to = 'images/'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


def get_video_path(instance, filename):
    extension = filename.split('.')[-1]
    return f'videos/{uuid4()}.{extension}'


class Media(DescribedModel, BaseModel):
    path_photo = models.ImageField(upload_to=path_and_rename, max_length=500, validators=[validate_file_size])
    path_video = models.FileField(
        upload_to=get_video_path, max_length=500, validators=[validate_video_file_size],
        default="",
        null=True, blank=True
    )

    def delete(self, *args, **kwargs):
        delete(self.path_photo)
        delete(self.path_video)
        super(Media, self).delete(*args, **kwargs)


class Field(DescribedModel):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children')
    is_static = models.BooleanField(default=False)
    point = models.IntegerField(default=0, null=True, blank=True)


class Taxonomy(DescribedModel, BaseModel):
    fields = models.ManyToManyField(Field, related_name='taxonomies')
    is_tag = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children')


class Stack(DescribedModel, BaseModel):
    medias = models.ManyToManyField(Media, related_name='stacks')
    taxonomies = models.ManyToManyField(Taxonomy, related_name='stacks')


class Round(BaseModel):
    CHOICE = (('first', _("First")), ('second', _("Second")), ('center', _("Center")))
    field = models.ForeignKey(Field, related_name='rounds', on_delete=models.CASCADE)
    first_value = models.CharField(max_length=500, null=True, blank=True)
    second_value = models.CharField(max_length=500, null=True, blank=True)
    conclusion = models.CharField(max_length=500, null=True, blank=True)
    winner = models.CharField(choices=CHOICE, default='center', max_length=10)


class Contribute(BaseModel):
    CHOICE = (('first', _("First")), ('second', _("Second")), ('center', _("Center")))
    auth_source = models.CharField(max_length=10, default='local')
    auth_id = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='contributes')

    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='contributes')
    position = models.CharField(choices=CHOICE, default='center', max_length=10)
    value = models.CharField(max_length=500, null=True, blank=True)


class Battle(DescribedModel, BaseModel):
    left = models.ForeignKey(Stack, on_delete=models.CASCADE, related_name='left_comparisons')
    right = models.ForeignKey(Stack, on_delete=models.CASCADE, related_name='right_comparisons')
    rounds = models.ManyToManyField(Round, related_name='battles')


class Vote(BaseModel):
    contribute = models.ForeignKey(Contribute, on_delete=models.CASCADE, related_name='votes')

    auth_source = models.CharField(max_length=10, default='local')
    auth_id = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='votes')
