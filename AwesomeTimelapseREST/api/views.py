from rest_framework import viewsets

from .serializers import VideoSerializer
from .models import Image, Video


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all().order_by('name')
    serializer_class = VideoSerializer


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by('name')
    serializer_class = VideoSerializer
