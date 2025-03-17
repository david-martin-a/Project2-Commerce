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
    self.listingObj = listingObj
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
    catList = listingObj.categories.all()
    catStr = ""
    if len(catList) > 0:
        for cat in catList:
            catStr = catStr + cat.category  + ", "
        # remove final comma in categories list
        catStr = catStr[:-2]
    else:
        catStr = "No categories listed"
    self.categories = catStr
    comments = Comments.objects.filter(comment_on=item_id)
    self.comments = comments


def index(request):    
    listings = Listings.objects.filter(active=True)
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
        # Determine which submit button was pressed in order to determine the course of action
        keys = form.data.keys()        
        if "place_bid" in keys:
            # the "Bid" button was clicked - check if bid amount was present and is a valid amount           
            if form.is_valid():
                amt = float(form.cleaned_data["amount"])                
                high_bid = float(request.POST["high_bid"])
                if int(request.POST["num_bids"]) > 0:
                    #this is NOT the first bit; it must be GREATER than the previous bid
                    if amt > high_bid:
                        new_bid = Bids(item_id=int(listing), bidder_id=request.user.id, amount=amt)
                        new_bid.save()
                        #listings = Listings.objects.all()
                        listingObj = Listings.objects.get(id=int(listing))
                        deets = ListingDetails(request.user.id, listing)
                        deets.msg = "Your bid was recorded."
                        return render(request, "auctions/listings.html", {
                            "listing": listingObj,
                            "details": deets    
                        })
                    else:
                        # the new bid was smaller than high bid - go back to same page with error message, vs errror page
                        listingObj = Listings.objects.get(id=int(listing))
                        deets = ListingDetails(request.user.id, listing)
                        deets.msg = "Error: Bid must be greater than the previous bid."
                        return render(request, "auctions/listings.html", {
                            "listing": listingObj,
                            "details": deets    
                        })
                else:
                    # num_bids is zero or not present; this bid can be GREATER OR EQUAL to reserve price
                    if amt >= high_bid:
                        new_bid = Bids(item_id=int(listing), bidder_id=request.user.id, amount=amt)
                        new_bid.save()
                        listings = Listings.objects.all()
                        return HttpResponseRedirect(request.path_info)                        
                    else:
                        # the new bid was smaller than high bid - go back to same page with error message, vs errror page
                        listingObj = Listings.objects.get(id=int(listing))
                        deets = ListingDetails(request.user.id, listing)
                        deets.msg = "Error: Bid must be greater than the previous bid."
                        return render(request, "auctions/listings.html", {
                            "listing": listingObj,
                            "details": deets    
                        })
            else:
                # The form was not valid - user may have entered value other than decimal
                listingObj = Listings.objects.get(id=int(listing))
                deets = ListingDetails(request.user.id, listing)
                deets.msg = "Error: Bid must be a valid two-digit number."
                return render(request, "auctions/listings.html", {
                    "listing": listingObj,
                    "details": deets    
                })
        elif "watch" in keys:
            # The "add to" or "remove from" watchlist button was pressed
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
                        # if listing was successfully removed from watchlist, refresh the page
                        return HttpResponseRedirect("/listings/" + listing)

        elif "close" in keys:
            # the "Close auction" button was clicked - change the item's active status to inactive
            return render(request, "auctions/message.html", {
                "message": "To be coded"
            })
        elif "add-comment" in keys:            
            new_comment = Comments(comment_by_id=request.user.id, comment_on_id=int(listing), comment=request.POST["comment"])
            try:
                new_comment.save()
            except IntegrityError:
                return render(request, "auctions/message.html", {
                    "message": "Error"
                })
            else:
                return HttpResponseRedirect("/listings/" + listing)        
        else:
            return render(request, "auctions/message.html", {
                "message": "Error"
            })
        
    else:
        # This is for GET method ----------------------------   
        listingObj = Listings.objects.get(id=int(listing))
        deets = ListingDetails(request.user.id, listing)
        return render(request, "auctions/listings.html", {
            "listing": listingObj,
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
    #user = request.user
    listings = Watch.objects.filter(watcher=request.user.id)
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

def category_list(request, category):
    categoryObj = Categories.objects.get(category=category)
    listings = categoryObj.listed.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "category": category
    }) 

def won(request):
    closed_auctions = Listings.objects.filter(active=False)
    # for each closed auction get the winning bid
    wins = []
    for auction in closed_auctions:
        bids = Bids.objects.filter(item=auction.id).order_by('amount').values()
        if bids.count() > 0:
            if bids[0]["bidder_id"] == request.user.id:
                wins.append(auction)

    return render(request, "auctions/index.html", {
        "listings": wins,
        "closed": True
    })


    # for each winning bid, check if it was made by user


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
