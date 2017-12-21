# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Show(models.Model):
    title = models.CharField(max_length=255)
    show_url = models.CharField(max_length=255)
    active = models.BooleanField(default=False)

class Season(models.Model):
    title = models.CharField(max_length=255)
    season_no = models.IntegerField()
    show = models.ForeignKey(Show)
    season_url = models.CharField(max_length=100)

class Episode(models.Model):
    show = models.ForeignKey(Show)
    season = models.ForeignKey(Season)
    episode_title  = models.CharField(max_length=100)
    episode_url = models.CharField(max_length=100)
    referrer_url = models.CharField(max_length=100)
    filename = models.CharField(max_length=100)
    file_format = models.CharField(max_length=10)
    save_location = models.CharField(max_length=100)
    download_size = models.IntegerField()
    download_timestamp = models.DateTimeField(auto_now_add=True)
    downloaded = models.BooleanField(default=False)

