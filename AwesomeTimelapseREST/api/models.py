from django.db import models


class Image(models.Model):
    data = models.ImageField(upload_to='images/')

    def __str__(self):
        return "Image Resource"


class Video(models.Model):
    name = models.CharField(max_length=60, null=False, unique=True)
    data = models.FileField(upload_to='videos/', null=True)

    def __str__(self):
        return self.name