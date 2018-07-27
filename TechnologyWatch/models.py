from datetime import timedelta

from django.core.validators import URLValidator, EmailValidator
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import User
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField(max_length=10, unique=True)
    picture_url = models.CharField(max_length=2000, default="/static/img/default_tag.png", validators=[URLValidator()])

    def __str__(self):
        return self.name

    def download_picture(self):
        pass


class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=2000)
    tags = models.ManyToManyField(Tag)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField("creation date", auto_now_add=True)

    def __str__(self):
        return self.name

    def get_time_ago(self):
        time_diff = timezone.now() - self.creation_date

        if time_diff < timedelta(hours=1):
            return "{} minutes".format(int(time_diff.seconds / 60))

        elif time_diff < timedelta(days=1):
            return "{} heures".format(int(time_diff.seconds / 3600))

        elif time_diff < timedelta(days=365):
            return "{} jours".format(time_diff.days)

        else:
            return "{} ans".format(time_diff.days // 365)

    def likes_count(self):
        return Like.objects.filter(topic=self).count()


class Resource(models.Model):
    name = models.CharField(max_length=100)
    link = models.CharField(max_length=2000, validators=[URLValidator()])
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return "{} ({})".format(self.name, self.link)


class Comment(models.Model):
    content = models.CharField(max_length=1000)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    post_date = models.DateTimeField("comment date", auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)


class Like(models.Model):
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    like_date = models.DateTimeField("like date", auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
