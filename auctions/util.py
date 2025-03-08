from django.db.models import Max
from .models import Bids, Listings

def get_high_bid(item_id):
  listingObj = Listings.objects.get(id=int(item_id))
  num_bids = Bids.objects.filter(item=int(item_id)).count()
  if num_bids > 0:        
      bid = Bids.objects.filter(item=int(item_id)).aggregate(Max("amount", default=0))        
      price = f"{bid['amount__max']:.2f}" 
  else:
      price = listingObj.reserve_price

  return price