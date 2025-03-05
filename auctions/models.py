from django.contrib.auth.models import AbstractUser
from django.db import models


class Users(AbstractUser):
    rating = models.CharField(max_length=32, blank=True, default="")
    postal_code = models.CharField(max_length=8, blank=True, default="")

class Categories(models.Model):
    category = models.CharField(max_length=64)

class Bids(models.Model):    
    bidder = models.ForeignKey(Users, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places = 2, max_digits=8)
    date = models.DateTimeField(auto_now_add=True)

class Listings(models.Model):
    vendor = models.ForeignKey(Users, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Categories)
    bids = models.ManyToManyField(Bids, blank=True, default="")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256, blank=True, default="")
    reserve_price = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    date_listed = models.DateTimeField(auto_now_add=True)
    img_link = models.URLField(blank=True, default="")
    active = models.BooleanField()

class Watch(models.Model):
    watcher = models.ForeignKey(Users, on_delete=models.CASCADE)
    item = models.ForeignKey(Listings, on_delete=models.CASCADE)    
    date = models.DateTimeField(auto_now_add=True)

class Comments(models.Model):
    comment_by = models.ForeignKey(Users, on_delete=models.CASCADE)
    comment_on = models.ForeignKey(Listings, on_delete=models.CASCADE)    
    comment = models.CharField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True)


