from django.db import models


class Image(models.Model):
    name = models.CharField(max_length=60)
    data = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.name


class Video(models.Model):
    name = models.CharField(max_length=60)
    data = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.name