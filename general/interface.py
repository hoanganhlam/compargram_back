from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone, text


class BaseModel(models.Model):
    STATUS_CHOICE = (
        (-1, _("Deleted")),
        (0, _("Pending")),
        (1, _("Active")),
    )

    updated = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(default=timezone.now)
    db_status = models.IntegerField(choices=STATUS_CHOICE, default=0)

    class Meta:
        abstract = True

    def save(self, **kwargs):
        # generate unique slug
        self.created = timezone.now()
        self.updated = timezone.now()
        super(BaseModel, self).save(**kwargs)


class DescribedModel(models.Model):
    title = models.CharField(max_length=120, unique=True)
    slug = models.CharField(max_length=120, unique=True)
    description = models.CharField(max_length=260, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(DescribedModel, self).__init__(*args, **kwargs)
        self.original_fields = self.__dict__.copy()

    def save(self, **kwargs):
        # generate unique slug
        self.slug = text.slugify(self.title)
        super(DescribedModel, self).save(**kwargs)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True
