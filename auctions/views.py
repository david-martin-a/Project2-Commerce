from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from . import util


from .models import User, Categories, Bids, Listings, Watch, Comments

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listings
        fields = ["categories", "title", "description", "reserve_price", "img_file", "active"]

class BidsForm(forms.ModelForm):
    class Meta:
        model = Bids
        fields = ["amount"]

class ListingDetails:
  
  def __init__(self, user_id, item_id):
    listingObj = Listings.objects.get(id=int(item_id))
    bids = Bids.objects.filter(item=int(item_id))
    self.num_bids = bids.count()
    if self.num_bids > 0:              
      max_bid = bids.aggregate(Max("amount", default=0))        
      self.high_bid = f"{max_bid['amount__max']:.2f}"
      max_bid_obj = Bids.objects.filter(amount=max_bid['amount__max'])
      if max_bid_obj[0].bidder.id == user_id:
        self.high_bidder = True
        if listingObj.active == False:
          self.winner = True
        else:
          self.winner = False
      else:
        self.high_bidder = False
    else:
        self.high_bid = listingObj.reserve_price
    i = Watch.objects.filter(watcher=int(user_id), item=int(item_id)).count()
    if i > 0:
      self.watched = True
    else:
      self.watched = False        

def index(request):    
    listings = Listings.objects.all()
    # get the high bid for each object
    for i in range(len(listings)):
        price = util.get_high_bid(listings[i].id)
        listings[i].reserve_price = price
    
    return render(request, "auctions/index.html", {
        "listings": listings
    })

def listings(request, listing):
    if request.method == "POST":
        form = BidsForm(request.POST)
        # Determine which submit button was pressed
        keys = form.data.keys()        
        if "place_bid" in keys:
            # the "Bid" button was clicked - check if bid amount was present and is a valid amount           
            if form.is_valid():
                amt = float(form.cleaned_data["amount"])                
                high_bid = float(request.POST["high_bid"])
                if amt > high_bid:
                    new_bid = Bids(item_id=int(listing), bidder_id=request.user.id, amount=amt)
                    new_bid.save()
                    listings = Listings.objects.all()
                    return HttpResponseRedirect(reverse(index))                        
                else:
                    # the new bid was smaller than high bid - go back to same page with error message, vs errror page
                    ...
            else:
                ...
        elif "watch" in keys:
            if form.data["watch"] == "1":
                new_watch = Watch(item_id=int(listing), watcher_id=request.user.id)            
                try:
                    new_watch.save()
                except IntegrityError:
                    return render(request, "auctions/message.html", {
                        "message": "Error"
                    })
                else:
                    util.update_user_number_watching(request)

                    #num = util.get_num_watching(request.user.id)
                    #request.user.number_on_watchlist = num
                    #request.user.save()
                    # if listing saved to user's watchlist successfully, refresh the page
                    return HttpResponseRedirect("/listings/" + listing)
            elif form.data["watch"] == "2":
                x = Watch.objects.filter(watcher_id=request.user.id, item_id=int(listing))
                if x.count() == 1:
                    try:
                        x.delete()
                    except IntegrityError:
                        return render(request, "auctions/message.html", {
                            "message": "Error"
                        })
                    else:
                        util.update_user_number_watching(request)
                        #num = util.get_num_watching(request.user.id)
                        #request.user.number_on_watchlist = num
                        #request.user.save()                                                
                        # if listing was successfully removed from watchlist, refresh the page
                        return HttpResponseRedirect("/listings/" + listing)

        elif "close" in keys:
            # the "Close" button was clicked - change the item's active status
            return render(request, "auctions/message.html", {
                "message": "To be coded"
            })
        
        else:
            return render(request, "auctions/message.html", {
                "message": "Error"
            })
        
    else:
        # This is for GET method ----------------------------    
        deets = ListingDetails(request.user.id, listing)
        listingObj = Listings.objects.get(id=int(listing))
        catList = listingObj.categories.all()
        catStr = ""
        if len(catList) > 0:
            for cat in catList:
                catStr = catStr + cat.category  + ", "
            # remove final comma in categories list
            catStr = catStr[:-2]
        else:
            catStr = "No categories listed"

        return render(request, "auctions/listings.html", {
            "listing": listingObj,
            "categories_str": catStr,
            "details": deets    
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
    
def watchlist(request):
    user = request.user
    listings = Watch.objects.filter(watcher=user.id)
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def edit(request, listing):
    ...

def message(request, message):
    return render(request, "auctions/message.html", {
        "message": message
    })

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
            # add number of items on their watchlist to user?
            num = util.get_num_watching(user.id)
            user.number_on_watchlist = num
            user.save()
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
