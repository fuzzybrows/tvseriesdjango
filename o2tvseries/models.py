# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Show(models.Model):
    title = models.CharField(max_length=255)
    base_url = models.CharField(max_length=255)
    active = models.BooleanField(default=False)

class Season(models.Model):
    title = models.CharField(max_length=255)
    show = models.ForeignKey(Show)

class Episode(models.Model):
    show = models.ForeignKey(Show)
    season = models.ForeignKey(Season)
    episode_no = models.CharField(max_length=50)
    episode_url = models.CharField(max_length=50)
    referrer_url = models.CharField(max_length=50)
    filename = models.CharField(max_length=50)
    download_size = models.IntegerField()
    download_timestamp = models.DateTimeField(auto_now_add=True)

