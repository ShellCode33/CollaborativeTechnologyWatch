from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=10, unique=True)
    picture_url = models.CharField(max_length=2000, default="/static/img/default_tag.png")

    def __str__(self):
        return self.name


class User(models.Model):
    pass


class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=2000)
    tags = models.ManyToManyField(Tag)
    #created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default="Inconnu")
    creation_date = models.DateTimeField("creation date", auto_now_add=True)

    def __str__(self):
        return self.name


# TODO : check valid link
class Resource(models.Model):
    name = models.CharField(max_length=100)
    link = models.CharField(max_length=2000)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return "{} ({})".format(self.name, self.link)


class Comment(models.Model):
    content = models.CharField(max_length=1000)
    # posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    post_date = models.DateTimeField("comment date", auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)


class Like(models.Model):
    # liked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    like_date = models.DateTimeField("like date", auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
