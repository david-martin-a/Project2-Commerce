from django.db.models import Max
from django.db import IntegrityError
from .models import Bids, Listings, Watch

def get_high_bid(item_id):
  listingObj = Listings.objects.get(id=int(item_id))
  num_bids = Bids.objects.filter(item=int(item_id)).count()
  if num_bids > 0:        
      bid = Bids.objects.filter(item=int(item_id)).aggregate(Max("amount", default=0))        
      price = f"{bid['amount__max']:.2f}" 
  else:
      price = listingObj.reserve_price

  return price

def get_num_watching(user_id):
  num = Watch.objects.filter(watcher=int(user_id)).count()
  if num > 0:
    return str(num)
  else:
    return "" 
   
def update_user_number_watching(request):
  num = Watch.objects.filter(watcher=int(request.user.id)).count()
  request.user.number_on_watchlist = num
  try:
    request.user.save()
  except IntegrityError:
    return False
  else:
    return True







