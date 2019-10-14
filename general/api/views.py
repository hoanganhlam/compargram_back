from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from general.models import Media
from general.api import serializers


# from datetime import datetime


class MediaViewSet(viewsets.ModelViewSet):
    models = Media
    queryset = models.objects.all().order_by('id')
    serializer_class = serializers.MediaSerializer
    permission_classes = permissions.AllowAny,
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    lookup_field = 'pk'
