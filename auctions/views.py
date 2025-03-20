from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponseRedirect
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
    # initialize the class object with all the details of the listing as viewed by a particular user
    listingObj = Listings.objects.get(id=int(item_id))
    self.listingObj = listingObj
    bids = Bids.objects.filter(item=int(item_id)).order_by("-amount")
    self.num_bids = bids.count()
    if self.num_bids > 0:  
      self.high_bid = f"{bids[0].amount:.2f}"
      if bids[0].bidder_id == user_id:
        self.high_bidder = True
        if listingObj.active == False:
          self.winner = True
        else:
          self.winner = False
      else:
        self.high_bidder = False
        self.winner = False
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
    listings = Listings.objects.filter(active=True).order_by("-date_listed")
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
                    #this is NOT the first bid; it must be GREATER than the previous bid
                    if amt > high_bid:
                        new_bid = Bids(item_id=int(listing), bidder_id=request.user.id, amount=amt)
                        new_bid.save() 
                        deets = ListingDetails(request.user.id, listing)
                        deets.msg = "Your bid was recorded."
                        return render(request, "auctions/listings.html", {                            
                            "details": deets    
                        })
                    else:
                        # the new bid was smaller than high bid - go back to same page with error message                        
                        deets = ListingDetails(request.user.id, listing)
                        deets.msg = "Error: Bid must be greater than the previous bid."
                        return render(request, "auctions/listings.html", {                            
                            "details": deets    
                        })
                else:
                    # This is the FIRST bid: (the num_bids is zero or not present) this bid can be greater OR EQUAL to reserve price
                    if amt >= high_bid:
                        new_bid = Bids(item_id=int(listing), bidder_id=request.user.id, amount=amt)
                        new_bid.save()
                        return HttpResponseRedirect(request.path_info)                        
                    else:
                        # the new bid was smaller than high bid - go back to same page with error message, vs errror page                        
                        deets = ListingDetails(request.user.id, listing)
                        deets.msg = "Error: Bid must be greater than or equal to the reserve price."
                        return render(request, "auctions/listings.html", {                            
                            "details": deets    
                        })
            else:
                # The form was not valid - user may have entered value other than decimal                
                deets = ListingDetails(request.user.id, listing)
                deets.msg = "Error: Bid must be a valid two-digit number."
                return render(request, "auctions/listings.html", {                    
                    "details": deets    
                })
        elif "watch" in keys:
            # The "add to" or "remove from" watchlist button was pressed
            if form.data["watch"] == "1":
                # It was the "add to" button that was pressed
                new_watch = Watch(item_id=int(listing), watcher_id=request.user.id)            
                try:
                    new_watch.save()
                except IntegrityError:
                    return render(request, "auctions/message.html", {
                        "message": "Error"
                    })
                else:
                    util.update_user_number_watching(request)
                    # if listing was successfully saved to user's watchlist, refresh the page
                    return HttpResponseRedirect("/listings/" + listing)
            elif form.data["watch"] == "2":
                # It was the "remove from" button that was pressed
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
            Listings.objects.filter(pk=int(listing)).update(active=False)            
            return HttpResponseRedirect(request.path_info)
        
        elif "add-comment" in keys:            
            new_comment = Comments(comment_by_id=request.user.id, comment_on_id=int(listing), comment=request.POST["comment"])
            try:
                new_comment.save()
            except IntegrityError:
                return render(request, "auctions/message.html", {
                    "message": "Error in saving comment"
                })
            else:
                return HttpResponseRedirect("/listings/" + listing)        
        else:
            # should never be triggered unless user changes form ids or values
            return render(request, "auctions/message.html", {
                "message": "Error"
            })        
    else:
        # This is for GET method ----------------------------  
        # User must be signed in 
        if request.user.id == None:
            return render(request, "auctions/message.html", {
                "message": "Please log in to view auction item details."
            }) 
        deets = ListingDetails(request.user.id, listing)
        return render(request, "auctions/listings.html", {            
            "details": deets    
        })

def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)        
        if form.is_valid():
            insert_listing = form.save(commit=False)
            # commit=False tells Django that "Don't send this to database yet.
            insert_listing.vendor = request.user # Set the user object here
            insert_listing.save() # Now you can send it to DB
            # save many-to-many items as a second step
            form.save_m2m()
            return render(request, "auctions/index.html", {
                "listings": Listings.objects.all()
            })           
        else:
            return render(request, "auctions/message.html", {
                "message": "Form data was not valid. Please try again"
            })
    else:
        # This section is for GET request for a blank "Create listing" form
        form = ListingForm()
        return render(request, "auctions/create.html", {
            "form": form
        })
    
def watchlist(request):    
    listings = Watch.objects.filter(watcher=request.user.id)
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

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
        # get the highest bid for each closed auction
        bids = Bids.objects.filter(item=auction.id).order_by('-amount').values()        
        if bids.count() > 0:
            if bids[0]["bidder_id"] == request.user.id:
                wins.append(auction)
    return render(request, "auctions/index.html", {
        "listings": wins,
        "closed": True
    })

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            # add number of items on the user's watchlist to user object instance
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
