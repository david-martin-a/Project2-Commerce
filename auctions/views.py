from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms


from .models import User, Categories, Bids, Listings, Watch, Comments

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listings
        fields = ["categories", "title", "description", "reserve_price", "img_file", "active"]

def index(request):    
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.all()
    })

def listings(request, listing):
    listingObj = Listings.objects.get(id=int(listing))
    return render(request, "auctions/listings.html", {
        "listing": listingObj
    })

def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        #form.vendor = request.user
        if form.is_valid():
            insert_listing = form.save(commit=False)
            # commit=False tells Django that "Don't send this to database yet.

            insert_listing.vendor = request.user # Set the user object here
            insert_listing.save() # Now you can send it to DB
            #form.save()
            form.save_m2m()
            return render(request, "auctions/index.html", {
                "listings": Listings.objects.all()
            })           
        else:
            ...



    else:
        # This section is for GET request
        form = ListingForm()
        return render(request, "auctions/create.html", {
            "form": form
        })

def edit(request, listing):
    ...

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Categories.objects.all()
    })    

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
