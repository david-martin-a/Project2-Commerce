from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    rating = models.CharField(max_length=32)
    postal_code = models.CharField(max_length=8)

class Category(models.Model):
    category_name = models.CharField(max_length=64)

class Bid(models.Model):    
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places = 2, max_digits=8)
    date = models.DateTimeField(auto_now_add=True)

class Listings(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)
    bids = models.ManyToManyField(Bid)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    reserve_price = models.DecimalField(decimal_places=2, max_digits=8)
    date_listed = models.DateTimeField()
    img_link = models.URLField()
    status = models.BooleanField()

class Watch(models.Model):
    watcher = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Listings, on_delete=models.CASCADE)    
    date = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_on = models.ForeignKey(Listings, on_delete=models.CASCADE)    
    comment = models.CharField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True)


