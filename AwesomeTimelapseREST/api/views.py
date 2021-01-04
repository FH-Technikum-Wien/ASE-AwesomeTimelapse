from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import ImageSerializer, VideoSerializer
from .models import Image, Video


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
