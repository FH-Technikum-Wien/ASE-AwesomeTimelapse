from django.db import models


class Image(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Video(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name