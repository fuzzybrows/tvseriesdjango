# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime

# Create your models here.

class Show(models.Model):
    title = models.CharField(max_length=255, unique=True, db_index=True)
    show_url = models.CharField(max_length=255)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Season(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    season_no = models.IntegerField(db_index=True)
    show = models.ForeignKey(Show)
    season_url = models.CharField(max_length=255)

    class Meta:
        unique_together = ('show', 'season_no', 'title')

    def __str__(self):
        return "{}:{}".format(self.show.title, self.title)

class Episode(models.Model):
    show = models.ForeignKey(Show)
    season = models.ForeignKey(Season)
    episode_title  = models.CharField(max_length=255, null=True, db_index=True)
    episode_url = models.CharField(max_length=255, null=True)
    episode_no = models.IntegerField(null=True)
    referrer_link = models.CharField(max_length=255, null=True)
    file_name = models.CharField(max_length=255, null=True)
    file_format = models.CharField(max_length=10, null=True)
    save_location = models.CharField(max_length=255, null=True)
    file_size = models.IntegerField(null=True)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    download_timestamp = models.DateTimeField(null=True)
    downloaded = models.BooleanField(default=False)

    class Meta:
        unique_together = ('show', 'season', 'episode_title')

    def __str__(self):
        return "{}:{}:{}".format(self.show.title, self.season.title, self.episode_title)

    def save(self, *args, **kwargs):
        if not self.download_timestamp and self.file_format and self.file_size and self.downloaded:
            self.download_timestamp = datetime.now()
        super(Episode, self).save(*args, **kwargs)
