from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    rating = models.CharField(max_length=32, blank=True, default="")
    postal_code = models.CharField(max_length=8, blank=True, default="")

class Categories(models.Model):
    category = models.CharField(max_length=64)

    class Meta:
        ordering = ["category"]

    def __str__(self):
        return f"{self.category}"

class Listings(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_listings")
    categories = models.ManyToManyField(Categories)    
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256, blank=True, default="")
    reserve_price = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    date_listed = models.DateTimeField(auto_now_add=True)
    img_file = models.CharField(max_length=64, blank=True, default="")
    active = models.BooleanField()

    def __str__(self):
        return f"{self.title}"  

class Bids(models.Model):  
    item = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="history")  
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places = 2, max_digits=8)
    date = models.DateTimeField(auto_now_add=True)  

class Watch(models.Model):
    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    item = models.ForeignKey(Listings, on_delete=models.CASCADE)    
    date = models.DateTimeField(auto_now_add=True)

class Comments(models.Model):
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    comment_on = models.ForeignKey(Listings, on_delete=models.CASCADE)    
    comment = models.CharField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True)


